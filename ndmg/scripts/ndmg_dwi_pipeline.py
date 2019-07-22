#!/usr/bin/env python
# Copyright 2019 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# ndmg_dwi_pipeline.py
# Repackaged for native space tractography by Derek Pisner in 2019
# Email: dpisner@utexas.edu



# standard library imports
import glob
import shutil
import os
import random
from argparse import ArgumentParser
from datetime import datetime
import time
import traceback
import sys
import warnings

warnings.simplefilter("ignore")

# pypi imports
# from ndmg.stats.qa_mri import qa_mri
import numpy as np
import nibabel as nib
from dipy.tracking.streamline import Streamlines
from dipy.tracking.utils import move_streamlines
from nilearn.image import new_img_like, resample_img

# local imports
import ndmg
from ndmg import preproc as mgp
from ndmg.scripts import ndmg_cloud as nc
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as rgu
from ndmg.utils import s3_utils
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.graph import gen_biggraph as ndbg
from ndmg.utils.bids_utils import name_resource
from ndmg.stats.qa_tensor import *
from ndmg.stats.qa_fibers import *

os.environ["MPLCONFIGDIR"] = "/tmp/"


def ndmg_dwi_pipeline(
    dwi,
    bvals,
    bvecs,
    t1w,
    atlas,
    mask,
    labels,
    outdir,
    vox_size,
    mod_type,
    track_type,
    mod_func,
    reg_style,
    clean,
    big,
    buck=None,
    remo=None,
    push=False,
    creds=None,
    debug=False,
    modif="",
):
    """Creates a brain graph from MRI data
    
    Parameters
    ----------
    dwi : str
        Location of dwi file(s)
    bvals : str
        Location of bval file(s)
    bvecs : str
        Location of bvec file(s)
    t1w : str
        Location of anatomical input file(s)
    atlas : str
        Location of atlas file
    mask : str
        Location of T1w brain mask file, make sure the proper voxel size is used
    labels : list
        Location of file containing the labels for the atlas file(s)
    outdir : str
        The directory where the output files should be stored. Prepopulate this folder with results of participants level analysis if running gorup analysis.
    vox_size : str
        Voxel size to use for template registrations. Default is '2mm'.
    mod_type : str
        Determinstic (det) or probabilistic (prob) tracking. Default is det.
    track_type : str
        Tracking approach: eudx or local. Default is eudx.
    mod_func : str
        Diffusion model: csd, csa, or tensor. Default is tensor.
    reg_style : str
        Space for tractography. Default is native.
    clean : bool
        Whether or not to delete intermediates. Default is False.
    big : bool
        Whether to produce big graphs for DWI, or voxelwise timeseries for fMRI.
    buck : str, optional
        The name of an S3 bucket which holds BIDS organized data. You musht have build your bucket with credentials to the S3 bucket you wish to access. Default is None
    remo : str, optional
        The path to the data on your S3 bucket. The data will be downloaded to the provided bids_dir on your machine. Default is None.
    push : bool, optional
        Flag to push derivatives back to S3. Default is False
    creds : bool, optional
        Determine if you have S3 credentials. Default is True
    debug : bool, optional
        If False, remove any old filed in the output directory. Default is False
    modif : str, optional
        Name of the folder on s3 to push to. If empty, push to a folder with ndmg's version number. Default is ""
    
    Returns
    -------
    [type]
        [description]
    
    Raises
    ------
    ValueError
        Raised if downsampling voxel size is not supported
    ValueError
        Raised if bval/bvecs are potentially corrupted
    """

    print('dwi = "{}"').format(dwi)
    print('bvals = "{}"').format(bvals)
    print('bvecs = "{}"').format(bvecs)
    print('t1w = "{}"').format(t1w)
    print('atlas = "{}"').format(atlas)
    print('mask = "{}"').format(mask)
    print("labels = {}").format(labels)
    print('outdir = "{}"').format(outdir)
    print('vox_size = "{}"').format(vox_size)
    print('mod_type = "{}"').format(mod_type)
    print('track_type = "{}"').format(track_type)
    print('mod_func = "{}"').format(mod_func)
    print('reg_style = "{}"').format(reg_style)
    print("clean = {}").format(clean)
    print("big = {}").format(big)
    startTime = datetime.now()
    fmt = "_adj.ssv"
    assert all(
        [
            dwi,
            bvals,
            bvecs,
            t1w,
            atlas,
            mask,
            labels,
            outdir,
            vox_size,
            mod_type,
            track_type,
            mod_func,
            reg_style,
        ]
    ), "Missing a default argument."

    # Put relevant file locations into one class
    namer = name_resource(dwi, t1w, atlas, outdir)

    print("Output directory: " + outdir)
    if not os.path.isdir(outdir):
        cmd = "mkdir -p {}".format(outdir)
        os.system(cmd)

    paths = {
        "prep_dwi": "dwi/preproc",
        "prep_anat": "anat/preproc",
        "reg_anat": "anat/registered",
        "tensor": "dwi/tensor",
        "fiber": "dwi/fiber",
        "voxelg": "dwi/voxel-connectomes",
        "conn": "dwi/roi-connectomes",
    }

    opt_dirs = ["prep_dwi", "prep_anat", "reg_anat"]
    clean_dirs = ["tensor", "fiber"]
    label_dirs = ["conn"]  # create label level granularity

    print("Adding directory tree...")
    namer.add_dirs_dwi(paths, labels, label_dirs)
    qc_stats = "{}/{}_stats.csv".format(
        namer.dirs["qa"]["adjacency"], namer.get_mod_source()
    )

    # Create derivative output file names
    streams = namer.name_derivative(namer.dirs["output"]["fiber"], "streamlines.trk")
    nodif_B0_iso_path = namer.name_derivative(
        namer.dirs["output"]["fiber"], "nodif_B0_iso.nii.gz"
    )
    streams_mni = namer.name_derivative(
        namer.dirs["output"]["fiber"], "streamlines_mni.trk"
    )

    if big:
        print("Generating voxelwise connectome...")
        voxel = namer.name_derivative(
            namer.dirs["output"]["voxelg"], "voxel-connectome.npz"
        )
        print("Voxelwise Fiber Graph: {}".format(voxel))

    # Again, connectomes are different
    if not isinstance(labels, list):
        labels = [labels]
    connectomes = [
        namer.name_derivative(
            namer.dirs["output"]["conn"][namer.get_label(lab)],
            "{}_{}_measure-spatial-ds{}".format(
                namer.get_mod_source(), namer.get_label(lab), fmt
            ),
        )
        for lab in labels
    ]

    print("Connectomes downsampled to given labels: " + ", ".join(connectomes))

    if vox_size == "1mm":
        zoom_set = (1.0, 1.0, 1.0)
    elif vox_size == "2mm":
        zoom_set = (2.0, 2.0, 2.0)
    else:
        raise ValueError("Voxel size not supported. Use 2mm or 1mm")

    # -------- Preprocessing Steps --------------------------------- #

    # Perform eddy correction
    start_time = time.time()
    if len(os.listdir(namer.dirs["output"]["prep_dwi"])) != 0:
        try:
            print("Pre-existing preprocessed dwi files found. Deleting these...")
            shutil.rmtree(namer.dirs["output"]["prep_dwi"])
            os.mkdir(namer.dirs["output"]["prep_dwi"])
        except Exception as e:
            print("Exception when trying to execute eddy correction: {}".format(e))
            pass

    dwi_prep = "{}/eddy_corrected_data.nii.gz".format(namer.dirs["output"]["prep_dwi"])
    eddy_rot_param = "{}/eddy_corrected_data.ecclog".format(
        namer.dirs["output"]["prep_dwi"]
    )
    print("Performing eddy correction...")
    cmd = "eddy_correct " + dwi + " " + dwi_prep + " 0"
    print(cmd)
    os.system(cmd)

    # Instantiate bvec/bval naming variations and copy to derivative director
    print("Instantiate bvec/bval naming variations, copy to derivative director")
    bvec_scaled = "{}/bvec_scaled.bvec".format(namer.dirs["output"]["prep_dwi"])
    fbval = "{}/bval.bval".format(namer.dirs["output"]["prep_dwi"])
    fbvec = "{}/bvec.bvec".format(namer.dirs["output"]["prep_dwi"])
    shutil.copyfile(bvecs, fbvec)
    shutil.copyfile(bvals, fbval)

    # Correct any corrupted bvecs/bvals
    print("Correcting corrupted bvals and bvecs")
    from dipy.io import read_bvals_bvecs

    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    bvecs[np.where(np.any(abs(bvecs) >= 10, axis=1) == True)] = [1, 0, 0]
    bvecs[np.where(bvals == 0)] = 0
    if (
        len(
            bvecs[
                np.where(
                    np.logical_and(
                        bvals > 50, np.all(abs(bvecs) == np.array([0, 0, 0]), axis=1)
                    )
                )
            ]
        )
        > 0
    ):
        raise ValueError(
            "WARNING: Encountered potentially corrupted bval/bvecs. Check to ensure volumes with a "
            "diffusion weighting are not being treated as B0's along the bvecs"
        )
    np.savetxt(fbval, bvals)
    np.savetxt(fbvec, bvecs)

    # Rescale bvecs
    print("Rescaling b-vectors...")
    mgp.rescale_bvec(fbvec, bvec_scaled)

    # Check orientation (dwi_prep)
    start_time = time.time()
    [dwi_prep, bvecs] = mgu.reorient_dwi(dwi_prep, bvec_scaled, namer)
    print(
        "%s%s%s"
        % ("Reorienting runtime: ", str(np.round(time.time() - start_time, 1)), "s")
    )

    # Check dimensions
    start_time = time.time()
    dwi_prep = mgu.match_target_vox_res(dwi_prep, vox_size, namer, sens="dwi")
    print(
        "%s%s%s"
        % ("Reslicing runtime: ", str(np.round(time.time() - start_time, 1)), "s")
    )

    # Build gradient table
    print("fbval: ", fbval)
    print("bvecs: ", bvecs)
    print("fbvec: ", fbvec)
    print("dwi_prep: ", dwi_prep)
    print("namer.dirs: ", namer.dirs["output"]["prep_dwi"])
    [gtab, nodif_B0, nodif_B0_mask] = mgu.make_gtab_and_bmask(
        fbval, fbvec, dwi_prep, namer.dirs["output"]["prep_dwi"]
    )

    # Get B0 header and affine
    dwi_prep_img = nib.load(dwi_prep)
    stream_affine = dwi_prep_img.affine
    hdr = dwi_prep_img.header
    print(
        "%s%s%s"
        % ("Preprocessing runtime: ", str(np.round(time.time() - start_time, 1)), "s")
    )

    # -------- Registration Steps ----------------------------------- #
    if len(os.listdir(namer.dirs["output"]["prep_anat"])) != 0:
        try:
            print("Pre-existing preprocessed t1w files found. Deleting these...")
            shutil.rmtree(namer.dirs["output"]["prep_anat"])
            os.mkdir(namer.dirs["output"]["prep_anat"])
        except:
            pass
    if len(os.listdir(namer.dirs["output"]["reg_anat"])) != 0:
        try:
            print("Pre-existing registered t1w files found. Deleting these...")
            shutil.rmtree(namer.dirs["output"]["reg_anat"])
            os.mkdir(namer.dirs["output"]["reg_anat"])
        except:
            pass
    if (len(os.listdir(namer.dirs["tmp"]["reg_a"])) != 0) or (
        len(os.listdir(namer.dirs["tmp"]["reg_m"])) != 0
    ):
        try:
            print("Pre-existing temporary files found. Deleting these...")
            shutil.rmtree(namer.dirs["tmp"]["reg_a"])
            os.mkdir(namer.dirs["tmp"]["reg_a"])
            shutil.rmtree(namer.dirs["tmp"]["reg_m"])
            os.mkdir(namer.dirs["tmp"]["reg_m"])
        except:
            pass

    # Check orientation (t1w)
    start_time = time.time()
    t1w = mgu.reorient_t1w(t1w, namer)
    print(
        "%s%s%s"
        % ("Reorienting runtime: ", str(np.round(time.time() - start_time, 1)), "s")
    )

    if reg_style == "native" or reg_style == "native_dsn":

        print("Running tractography in native space...")
        # Instantiate registration
        reg = mgr.dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w, vox_size, simple=False)
        # Perform anatomical segmentation
        start_time = time.time()
        reg.gen_tissue()
        print(
            "%s%s%s"
            % ("gen_tissue runtime: ", str(np.round(time.time() - start_time, 1)), "s")
        )

        # Align t1w to dwi
        start_time = time.time()
        reg.t1w2dwi_align()
        print(
            "%s%s%s"
            % (
                "t1w2dwi_align runtime: ",
                str(np.round(time.time() - start_time, 1)),
                "s",
            )
        )

        # Align tissue classifiers
        start_time = time.time()
        reg.tissue2dwi_align()
        print(
            "%s%s%s"
            % (
                "tissue2dwi_align runtime: ",
                str(np.round(time.time() - start_time, 1)),
                "s",
            )
        )

        # -------- Tensor Fitting and Fiber Tractography ---------------- #

        # TODO: these are the same commands
        if track_type == "eudx":
            seeds = mgt.build_seed_list(reg.wm_gm_int_in_dwi, np.eye(4), dens=3)
        else:
            seeds = mgt.build_seed_list(reg.wm_gm_int_in_dwi, np.eye(4), dens=3)
        print("Using " + str(len(seeds)) + " seeds...")

        # Compute direction model and track fiber streamlines
        print("Beginning tractography...")
        trct = mgt.run_track(
            dwi_prep,
            nodif_B0_mask,
            reg.gm_in_dwi,
            reg.vent_csf_in_dwi,
            reg.csf_mask_dwi,
            reg.wm_in_dwi,
            gtab,
            mod_type,
            track_type,
            mod_func,
            seeds,
            np.eye(4),
        )
        streamlines = trct.run()
        streamlines = Streamlines([sl for sl in streamlines if len(sl) > 60])
        print("Streamlines complete")

        if reg_style == "native_dsn":
            # Save streamlines to disk
            print("Saving streamlines: " + streams)

            def transform_to_affine(streams, header, affine):
                rotation, scale = np.linalg.qr(affine)
                streams = move_streamlines(streams, rotation)
                scale[0:3, 0:3] = np.dot(
                    scale[0:3, 0:3], np.diag(1.0 / header["voxel_sizes"])
                )
                scale[0:3, 3] = abs(scale[0:3, 3])
                streams = move_streamlines(streams, scale)
                return streams

            trk_affine = np.eye(4)
            B0_img = nib.load(nodif_B0)
            B0_affine = B0_img.affine
            trk_hdr = nib.streamlines.trk.TrkFile.create_empty_header()
            trk_hdr["hdr_size"] = 1000
            trk_hdr["dimensions"] = hdr["dim"][1:4].astype("float32")
            trk_hdr["voxel_sizes"] = hdr["pixdim"][1:4]
            trk_hdr["voxel_to_rasmm"] = trk_affine
            trk_hdr["voxel_order"] = "LPS"
            trk_hdr["pad2"] = "LPS"
            trk_hdr["image_orientation_patient"] = np.array(
                [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
            ).astype("float32")
            trk_hdr["endianness"] = "<"
            trk_hdr["_offset_data"] = 1000
            trk_hdr["nb_streamlines"] = streamlines.total_nb_rows
            streamlines_trans = Streamlines(
                transform_to_affine(streamlines, trk_hdr, B0_affine)
            )
            tractogram = nib.streamlines.Tractogram(
                streamlines, affine_to_rasmm=trk_affine
            )
            trkfile = nib.streamlines.trk.TrkFile(tractogram, header=trk_hdr)
            nib.streamlines.save(trkfile, streams)

            # Normalize streamlines
            print("Running DSN...")
            streams_warp = mgr.direct_streamline_norm(
                streams, streams_mni, nodif_B0, namer
            )

            # Read Streamlines
            streamlines_mni = nib.streamlines.load(streams_warp).streamlines
            streamlines = Streamlines(streamlines_mni)

    elif reg_style == "mni":

        # Check dimensions
        start_time = time.time()
        t1w = mgu.match_target_vox_res(t1w, vox_size, namer, sens="t1w")
        print(
            "%s%s%s"
            % ("Reslicing runtime: ", str(np.round(time.time() - start_time, 1)), "s")
        )
        print("Running tractography in MNI-space...")
        aligned_dwi = "{}/dwi_mni_aligned.nii.gz".format(
            namer.dirs["output"]["prep_dwi"]
        )

        # Align DWI volumes to Atlas
        print("Aligning volumes...")
        reg = mgr.dmri_reg_old(dwi_prep, gtab, t1w, atlas, aligned_dwi, namer, clean)
        print("Registering DWI image at {} to atlas; aligned dwi at {}...").format(
            dwi_prep, aligned_dwi
        )  # alex  # TODO: make sure dwi_prep is what is being registered
        reg.dwi2atlas()

        # -------- Tensor Fitting and Fiber Tractography ---------------- #
        print("Beginning tractography...")
        # Compute tensors and track fiber streamlines
        print("aligned_dwi: {}").format(aligned_dwi)
        print("gtab: {}").format(gtab)
        [tens, streamlines, align_dwi_mask] = mgt.eudx_basic(
            aligned_dwi, gtab, stop_val=0.2
        )
        tensors = "{}/tensors.nii.gz".format(namer.dirs["output"]["tensor"])
        tensor2fa(
            tens,
            tensors,
            aligned_dwi,
            namer.dirs["output"]["tensor"],
            namer.dirs["qa"]["tensor"],
        )

        # Save streamlines to disk
        print("Saving streamlines: " + streams)
        print("streamlines: {}").format(streamlines)
        print("streams: {}").format(streams)
        tractogram_list = [i for i in streamlines]  # alex
        trk_affine = np.diagflat(
            [1, 1, 1, 1]
        )  # alex  # TODO: remove in favor of something not hardcoded
        tractogram = nib.streamlines.Tractogram(
            tractogram_list, affine_to_rasmm=trk_affine
        )  # alex
        nib.streamlines.save(tractogram, streams)  # alex
        streamlines = Streamlines(
            streamlines
        )  # alex  # to try to make the streamlines variable be the same thing as the native space one
        print("atlas location: {}").format(atlas)
        print("affine: {}").format(trk_affine)

    # -------- Big Graph Generation --------------------------------- #
    # Generate big graphs from streamlines
    if big is True:
        print("Making Voxelwise Graph...")
        bg1 = ndbg.biggraph()
        bg1.make_graph(streamlines)
        bg1.save_graph(voxel)

    # ------- Connectome Estimation --------------------------------- #
    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(labels):
        print("Generating graph for {} parcellation...".format(label))
        if reg_style == "native_dsn":
            # align atlas to t1w to dwi
            print("%s%s" % ("Applying native-space alignment to ", labels[idx]))
            labels_im_file = mgu.match_target_vox_res(
                labels[idx], vox_size, namer, sens="t1w"
            )
            labels_im_file_mni = reg.atlas2t1w2dwi_align(labels_im_file, dsn=True)
            labels_im = nib.load(labels_im_file_mni)
            g1 = mgg.graph_tools(
                attr=len(np.unique(labels_im.get_data().astype("int"))) - 1,
                rois=labels_im_file_mni,
                tracks=streamlines,
                affine=np.eye(4),
                namer=namer,
                connectome_path=connectomes[idx],
            )
            g1.make_graph_old()
        elif reg_style == "native":
            # align atlas to t1w to dwi
            print("%s%s" % ("Applying native-space alignment to ", labels[idx]))
            labels_im_file = mgu.match_target_vox_res(
                labels[idx], vox_size, namer, sens="t1w"
            )
            labels_im_file_dwi = reg.atlas2t1w2dwi_align(labels_im_file, dsn=False)
            labels_im = nib.load(labels_im_file_dwi)
            g1 = mgg.graph_tools(
                attr=len(np.unique(labels_im.get_data().astype("int"))) - 1,
                rois=labels_im_file_dwi,
                tracks=streamlines,
                affine=np.eye(4),
                namer=namer,
                connectome_path=connectomes[idx],
            )
            g1.make_graph_old()
        elif reg_style == "mni":
            labels_im_file = mgu.match_target_vox_res(
                labels[idx], vox_size, namer, sens="t1w"
            )
            labels_im = nib.load(labels_im_file)
            g1 = mgg.graph_tools(
                attr=len(np.unique(labels_im.get_data().astype("int"))) - 1,
                rois=labels_im_file,
                tracks=streamlines,
                affine=np.eye(4),
                namer=namer,
                connectome_path=connectomes[idx],
            )
            g1.make_graph_old()
        g1.summary()
        g1.save_graph(connectomes[idx])

    exe_time = datetime.now() - startTime

    print("Total execution time: {}".format(exe_time))
    print("NDMG Complete.")

    # TODO : putting this block of code here for now because it wouldn't run in `ndmg_bids`. Figure out how to put it somewhere else.
    if push and buck and remo is not None:
        if not modif:
            modif = "ndmg_{}".format(ndmg.version.replace(".", "-"))
        s3_utils.s3_push_data(buck, remo, outdir, modif, creds, debug=debug)
        print("Pushing Complete!")
        if not debug:
            print("Listing contents of output directory ...")
            print(os.listdir(outdir))
            print("clearing contents of output directory ...")
            shutil.rmtree(outdir)
            print(
                "Clearing complete. Output directory exists: {}".format(
                    os.path.exists(outdir)
                )
            )
            # # Log docker info in EC2 containers, assuming we're using AWS Batch
            # f = subprocess.check_output('docker info', shell=True)
            # info_we_care_about = f[f.find(
            #     'Data Space Used'):f.find('Metadata Space Used')]
            # print("docker info on space: {}".format(info_we_care_about))
    sys.exit(0)


def main():
    parser = ArgumentParser(
        description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images"
    )
    parser.add_argument("dwi", action="store", help="Nifti DTI image stack")
    parser.add_argument("bval", action="store", help="DTI scanner b-values")
    parser.add_argument("bvec", action="store", help="DTI scanner b-vectors")
    parser.add_argument("t1w", action="store", help="Nifti T1w MRI image")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument(
        "mask",
        action="store",
        help="Nifti binary mask of \
                        brain space in the atlas",
    )
    parser.add_argument(
        "outdir",
        action="store",
        help="Path to which \
                        derivatives will be stored",
    )
    parser.add_argument(
        "labels",
        action="store",
        nargs="*",
        help="Nifti \
                        labels of regions of interest in atlas space",
    )
    parser.add_argument(
        "--vox",
        action="store",
        nargs="*",
        default="1mm",
        help="Voxel size to use for template registrations \
                        (e.g. '1mm')",
    )
    parser.add_argument(
        "--mod",
        action="store",
        help="Determinstic (det) or probabilistic (prob) tracking. Default is det.",
        default="det",
    )
    parser.add_argument(
        "--tt",
        action="store",
        help="Tracking approach: eudx or local. Default is eudx.",
        default="eudx",
    )
    parser.add_argument(
        "--mf",
        action="store",
        help="Diffusion model: csd, csa, or tensor. Default is tensor.",
        default="tensor",
    )
    parser.add_argument(
        "--sp",
        action="store",
        help="Space for tractography. Default is native.",
        default="native",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Whether or not to delete intemediates",
    )
    parser.add_argument(
        "-b",
        "--big",
        action="store_true",
        default=False,
        help="whether or not to produce voxelwise big graph",
    )
    result = parser.parse_args()

    # Create output directory
    print("Creating output directory: {}".format(result.outdir))
    print("Creating output temp directory: {}/tmp".format(result.outdir))
    mgu.utils.execute_cmd("mkdir -p {} {}/tmp".format(result.outdir, result.outdir))

    ndmg_dwi_pipeline(
        result.dwi,
        result.bval,
        result.bvec,
        result.t1w,
        result.atlas,
        result.mask,
        result.labels,
        result.outdir,
        result.vox,
        result.mod,
        result.tt,
        result.mf,
        result.sp,
        result.clean,
        result.big,
    )


if __name__ == "__main__":
    main()
