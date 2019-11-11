#!/usr/bin/env python

"""
ndmg.scripts.ndmg_dwi_pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains the primary, top-level pipeline.
For a full description, see here: https://neurodata.io/talks/ndmg.pdf
"""


# standard library imports
import shutil
import time
from datetime import datetime
import os

# package imports
import nibabel as nib
import numpy as np
from subprocess import Popen
from dipy.tracking.streamline import Streamlines
from dipy.io import read_bvals_bvecs

# ndmg imports
from ndmg import preproc
from ndmg import register
from ndmg import track
from ndmg import graph
from ndmg.utils import gen_utils
from ndmg.utils import reg_utils
from ndmg.utils import cloud_utils

# TODO : not sure why this is here, potentially remove
os.environ["MPLCONFIGDIR"] = "/tmp/"


def ndmg_dwi_worker(
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
    seeds,
    reg_style,
    skipeddy=False,
    skipreg=False,
    buck=None,
    remo=None,
    push=False,
    creds=None,
    modif="",
    skull="none",
):
    """Creates a brain graph from MRI data

    Parameters
    ----------
    dwi : str
        Path for the dwi file(s)
    bvals : str
        Path for the bval file(s)
    bvecs : str
        Path for the bvec file(s)
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
    seeds : int
        Density of seeding for native-space tractography.
    reg_style : str
        Space for tractography. Default is native.
    skipeddy : bool
        Whether or not to skip the eddy correction if it has already been run. Default is False.
    skipreg : bool
        Whether or not to skip registration. Default is False.
    buck : str, optional
        The name of an S3 bucket which holds BIDS organized data. You musht have build your bucket with credentials to the S3 bucket you wish to access. Default is None
    remo : str, optional
        The path to the data on your S3 bucket. The data will be downloaded to the provided bids_dir on your machine. Default is None.
    push : bool, optional
        Flag to push derivatives back to S3. Default is False
    creds : bool, optional
        Determine if you have S3 credentials. Default is True
    modif : str, optional
        Name of the folder on s3 to push to. If empty, push to a folder with ndmg's version number. Default is ""
    skull : str, optional
        skullstrip parameter pre-set. Default is "none".

    Raises
    ------
    ValueError
        Raised if downsampling voxel size is not supported
    ValueError
        Raised if bval/bvecs are potentially corrupted
    """
    print(f"dwi = {dwi}")
    print(f"bvals = {bvals}")
    print(f"bvecs = {bvecs}")
    print(f"t1w = {t1w}")
    print(f"atlas = {atlas}")
    print(f"mask = {mask}")
    print(f"labels = {labels}")
    print(f"outdir = {outdir}")
    print(f"vox_size = {vox_size}")
    print(f"mod_type = {mod_type}")
    print(f"track_type = {track_type}")
    print(f"mod_func = {mod_func}")
    print(f"seeds = {seeds}")
    print(f"reg_style = {reg_style}")
    print(f"skipeddy = {skipeddy}")
    print(f"skipreg = {skipreg}")
    print(f"skull = {skull}")
    fmt = "_adj.csv"

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
            seeds,
            reg_style,
        ]
    ), "Missing a default argument."

    startTime = datetime.now()

    namer = gen_utils.NameResource(dwi, t1w, atlas, outdir)

    # TODO : do this with shutil instead of an os command
    print("Output directory: " + outdir)
    if not os.path.isdir(outdir):
        cmd = f"mkdir -p {outdir}"
        os.system(cmd)

    paths = {
        "prep_dwi": "dwi/preproc",
        "prep_anat": "anat/preproc",
        "reg_anat": "anat/registered",
        "fiber": "dwi/fiber",
        "tensor": "dwi/tensor",
        "conn": "dwi/roi-connectomes",
    }

    label_dirs = ["conn"]  # create label level granularity

    print("Adding directory tree...")
    namer.add_dirs(paths, labels, label_dirs)

    # Create derivative output file names
    streams = namer.name_derivative(namer.dirs["output"]["fiber"], "streamlines.trk")

    # generate list of connectomes
    labels = gen_utils.as_list(labels)
    connectomes = [
        namer.name_derivative(
            namer.dirs["output"]["conn"][namer.get_label(lab)],
            f"{namer.get_mod_source()}_{namer.get_label(lab)}_measure-spatial-ds{fmt}",
        )
        for lab in labels
    ]

    warm_welcome = welcome_message(connectomes)
    print(warm_welcome)

    if vox_size != "1mm" and vox_size != "2mm":
        raise ValueError("Voxel size not supported. Use 2mm or 1mm")

    # -------- Preprocessing Steps --------------------------------- #

    # Perform eddy correction
    dwi_prep = f'{namer.dirs["output"]["prep_dwi"]}/eddy_corrected_data.nii.gz'

    if len(os.listdir(namer.dirs["output"]["prep_dwi"])) != 0:
        if skipeddy is False:
            try:
                print("Pre-existing preprocessed dwi files found. Deleting these...")
                shutil.rmtree(namer.dirs["output"]["prep_dwi"])
                os.mkdir(namer.dirs["output"]["prep_dwi"])
            except Exception as e:
                print(f"Exception when trying to delete existing data: {e}")
                pass
            print("Performing eddy correction...")
            cmd = "eddy_correct " + dwi + " " + dwi_prep + " 0"
            print(cmd)
            sts = Popen(cmd, shell=True).wait()
            print(sts)
            ts = time.time()
            st = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            print(st)
        else:
            if not os.path.isfile(dwi_prep):
                raise ValueError(
                    "ERROR: Cannot skip eddy correction if it has not already been run!"
                )
    else:
        print("Performing eddy correction...")
        cmd = "eddy_correct " + dwi + " " + dwi_prep + " 0"
        print(cmd)
        sts = Popen(cmd, shell=True).wait()
        print(sts)
        ts = time.time()
        st = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        print(st)

    # Instantiate bvec/bval naming variations and copy to derivative director
    bvec_scaled = f'{namer.dirs["output"]["prep_dwi"]}/bvec_scaled.bvec'
    fbval = f'{namer.dirs["output"]["prep_dwi"]}/bval.bval'
    fbvec = f'{namer.dirs["output"]["prep_dwi"]}/bvec.bvec'
    shutil.copyfile(bvecs, fbvec)
    shutil.copyfile(bvals, fbval)

    # Correct any corrupted bvecs/bvals
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
    preproc.rescale_bvec(fbvec, bvec_scaled)

    # Check orientation (dwi_prep)
    [dwi_prep, bvecs] = gen_utils.reorient_dwi(dwi_prep, bvec_scaled, namer)

    # Check dimensions
    dwi_prep = gen_utils.match_target_vox_res(dwi_prep, vox_size, namer, sens="dwi")

    # Build gradient table
    print("fbval: ", fbval)
    print("bvecs: ", bvecs)
    print("fbvec: ", fbvec)
    print("dwi_prep: ", dwi_prep)
    print("namer.dirs: ", namer.dirs["output"]["prep_dwi"])
    [gtab, nodif_B0, nodif_B0_mask] = gen_utils.make_gtab_and_bmask(
        fbval, fbvec, dwi_prep, namer.dirs["output"]["prep_dwi"]
    )

    # Get B0 header and affine
    dwi_prep_img = nib.load(dwi_prep)
    hdr = dwi_prep_img.header

    # -------- Registration Steps ----------------------------------- #
    if (skipreg is False) and len(os.listdir(namer.dirs["output"]["prep_anat"])) != 0:
        try:
            print("Pre-existing preprocessed t1w files found. Deleting these...")
            shutil.rmtree(namer.dirs["output"]["prep_anat"])
            os.mkdir(namer.dirs["output"]["prep_anat"])
        except:
            pass
    if (skipreg is False) and len(os.listdir(namer.dirs["output"]["reg_anat"])) != 0:
        try:
            print("Pre-existing registered t1w files found. Deleting these...")
            shutil.rmtree(namer.dirs["output"]["reg_anat"])
            os.mkdir(namer.dirs["output"]["reg_anat"])
        except:
            pass
    if (skipreg is False) and (
        (len(os.listdir(namer.dirs["tmp"]["reg_a"])) != 0)
        or (len(os.listdir(namer.dirs["tmp"]["reg_m"])) != 0)
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
    t1w = gen_utils.reorient_img(t1w, namer)
    t1w = gen_utils.match_target_vox_res(t1w, vox_size, namer, sens="t1w")

    if reg_style == "native" or reg_style == "native_dsn":

        print("Running registration in native space...")

        # Instantiate registration
        reg = register.DmriReg(
            namer, nodif_B0, nodif_B0_mask, t1w, vox_size, skull, simple=False
        )

        # Perform anatomical segmentation
        if (skipreg is True) and os.path.isfile(reg.wm_edge):
            print("Found existing gentissue run!")
        else:
            reg.gen_tissue()

        # Align t1w to dwi
        if (
            (skipreg is True)
            and os.path.isfile(reg.t1w2dwi)
            and os.path.isfile(reg.mni2t1w_warp)
            and os.path.isfile(reg.t1_aligned_mni)
        ):
            print("Found existing t1w2dwi run!")
        else:
            reg.t1w2dwi_align()

        # Align tissue classifiers
        if (
            (skipreg is True)
            and os.path.isfile(reg.wm_gm_int_in_dwi)
            and os.path.isfile(reg.vent_csf_in_dwi)
            and os.path.isfile(reg.corpuscallosum_dwi)
        ):
            print("Found existing tissue2dwi run!")
        else:
            reg.tissue2dwi_align()

        # Align atlas to dwi-space and check that the atlas hasn't lost any of the rois
        if reg_style == "native_dsn":
            labels_im_file_mni_list = reg_utils.skullstrip_check(
                reg, labels, namer, vox_size, reg_style
            )
        elif reg_style == "native":
            labels_im_file_dwi_list = reg_utils.skullstrip_check(
                reg, labels, namer, vox_size, reg_style
            )

        # -------- Tensor Fitting and Fiber Tractography ---------------- #
        start_time = time.time()
        seeds = track.build_seed_list(reg.wm_gm_int_in_dwi, np.eye(4), dens=int(seeds))
        print("Using " + str(len(seeds)) + " seeds...")

        # Compute direction model and track fiber streamlines
        print("Beginning tractography in native space...")
        trct = track.RunTrack(
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

        trk_affine = np.eye(4)
        trk_hdr = nib.streamlines.trk.TrkFile.create_empty_header()
        trk_hdr["hdr_size"] = 1000
        trk_hdr["dimensions"] = hdr["dim"][1:4].astype("float32")
        trk_hdr["voxel_sizes"] = hdr["pixdim"][1:4]
        trk_hdr["voxel_to_rasmm"] = trk_affine
        trk_hdr["voxel_order"] = "RAS"
        trk_hdr["pad2"] = "RAS"
        trk_hdr["image_orientation_patient"] = np.array(
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ).astype("float32")
        trk_hdr["endianness"] = "<"
        trk_hdr["_offset_data"] = 1000
        trk_hdr["nb_streamlines"] = streamlines.total_nb_rows
        tractogram = nib.streamlines.Tractogram(streamlines, affine_to_rasmm=trk_affine)
        trkfile = nib.streamlines.trk.TrkFile(tractogram, header=trk_hdr)
        nib.streamlines.save(trkfile, streams)
        print(
            "%s%s%s"
            % (
                "Tractography runtime: ",
                str(np.round(time.time() - start_time, 1)),
                "s",
            )
        )

    if reg_style == "native_dsn":

        fa_path = track.tens_mod_fa_est(gtab, dwi_prep, nodif_B0_mask)

        # Normalize streamlines
        print("Running DSN...")
        [streamlines_mni, streams_mni] = register.direct_streamline_norm(
            streams, fa_path, namer
        )

        # Save streamlines to disk
        print("Saving DSN-registered streamlines: " + streams_mni)

    # TODO : mni space currently broken. Fix EuDX in track.py.
    # elif reg_style == "mni":
    #     # Check dimensions
    #     start_time = time.time()
    #     t1w = gen_utils.match_target_vox_res(
    #         t1w, vox_size, namer, sens="t1w"
    #     )  # this is the second time this t1w data has been sent to this function (REMOVE?)
    #     print(
    #         "%s%s%s"
    #         % ("Reslicing runtime: ", str(np.round(time.time() - start_time, 1)), "s")
    #     )
    #     print("Running tractography in MNI-space...")
    #     aligned_dwi = "{}/dwi_mni_aligned.nii.gz".format(
    #         namer.dirs["output"]["prep_dwi"]
    #     )

    #     # Align DWI volumes to Atlas
    #     print("Aligning volumes...")
    #     reg = register.DmriRegOld(dwi_prep, gtab, t1w, mask, aligned_dwi, namer, clean=False)
    #     print(
    #         "Registering DWI image at {} to atlas; aligned dwi at {}...".format(
    #             dwi_prep, aligned_dwi
    #         )
    #     )
    #     reg.dwi2atlas()

    #     # -------- Tensor Fitting and Fiber Tractography ---------------- #
    #     print("Beginning tractography...")
    #     # Compute tensors and track fiber streamlines
    #     print("aligned_dwi: {}".format(aligned_dwi))
    #     print("gtab: {}".format(gtab))
    #     [tens, streamlines, align_dwi_mask] = track.eudx_basic(
    #         aligned_dwi, gtab, stop_val=0.2
    #     )
    #     tensors = "{}/tensors.nii.gz".format(namer.dirs["output"]["tensor"])
    #     tensor2fa(
    #         tens,
    #         tensors,
    #         aligned_dwi,
    #         namer.dirs["output"]["tensor"],
    #         namer.dirs["qa"]["tensor"],
    #     )

    #     # Save streamlines to disk
    #     print("Saving streamlines: " + streams)
    #     print("streamlines: {}".format(streamlines))
    #     print("streams: {}".format(streams))
    #     tractogram_list = [i for i in streamlines]
    #     trk_affine = np.eye(4)
    #     tractogram = nib.streamlines.Tractogram(
    #         tractogram_list, affine_to_rasmm=trk_affine
    #     )
    #     nib.streamlines.save(tractogram, streams)
    #     streamlines = Streamlines(
    #         streamlines
    #     )  # alex  # to try to make the streamlines variable be the same thing as the native space one
    #     print("atlas location: {}".format(atlas))

    # ------- Connectome Estimation --------------------------------- #
    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(labels):
        print(f"Generating graph for {label} parcellation...")
        if reg_style == "native_dsn":
            # align atlas to t1w to dwi
            print(f"Applying native-space alignment to {labels[idx]}")
            labels_im = nib.load(labels_im_file_mni_list[idx])
            g1 = graph.GraphTools(
                attr=len(np.unique(np.around(labels_im.get_data()).astype("int16")))
                - 1,
                rois=labels_im_file_mni_list[idx],
                tracks=streamlines_mni,
                affine=np.eye(4),
                namer=namer,
                connectome_path=connectomes[idx],
            )
            g1.g = g1.make_graph()
        elif reg_style == "native":
            # align atlas to t1w to dwi
            print(f"Applying native-space alignment to {labels[idx]}")
            labels_im = nib.load(labels_im_file_dwi_list[idx])
            g1 = graph.GraphTools(
                attr=len(np.unique(np.around(labels_im.get_data()).astype("int16")))
                - 1,
                rois=labels_im_file_dwi_list[idx],
                tracks=streamlines,
                affine=np.eye(4),
                namer=namer,
                connectome_path=connectomes[idx],
            )
            g1.g = g1.make_graph()

        # TODO : mni-space currently broken. Fix in track.
        # elif reg_style == "mni":
        #     labels_im_file = gen_utils.reorient_img(labels[idx], namer)
        #     labels_im_file = gen_utils.match_target_vox_res(
        #         labels_im_file, vox_size, namer, sens="t1w"
        #     )
        #     labels_im = nib.load(labels_im_file)
        #     g1 = graph.graph_tools(
        #         attr=len(np.unique(np.around(labels_im.get_data()).astype("int16")))
        #         - 1,
        #         rois=labels_im_file,
        #         tracks=streamlines,
        #         affine=np.eye(4),
        #         namer=namer,
        #         connectome_path=connectomes[idx],
        #     )
        #     g1.make_graph_old()
        g1.summary()
        g1.save_graph_png(connectomes[idx])
        g1.save_graph(connectomes[idx])

    exe_time = datetime.now() - startTime

    print(f"Total execution time: {exe_time}")
    print("NDMG Complete.")

    if reg_style == "native" or reg_style == "native_dsn":
        print(
            "NOTE :: you are using native-space registration to generate connectomes. \
             Without post-hoc normalization, multiple connectomes generated with NDMG \
             cannot be compared directly."
        )

    if push and buck and remo is not None:
        if not modif:
            modif = "ndmg_{}".format(__version__.replace(".", "-"))
        cloud_utils.s3_push_data(buck, remo, outdir, modif, creds)
        print("Pushing Complete!")


def welcome_message(connectomes):

    line = """\n~~~~~~~~~~~~~~~~\n 
    Welcome to ndmg!\n 
    Your connectomes will be located here:
    \n\n"""

    for connectome in connectomes:
        line += connectome + "\n"

    line += "~~~~~~~~~~~~~~~~\n"

    return line


def main():
    parser = ArgumentParser(
        description="This is an end-to-end connectome estimation pipeline from sMRI and DTI images"
    )
    parser.add_argument("dwi", action="store", help="Nifti dMRI image stack")
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
        "-sked",
        "--sked",
        action="store_true",
        default=False,
        help="whether or not to skip eddy correction",
    )
    parser.add_argument(
        "-skreg",
        "--skreg",
        action="store_true",
        default=False,
        help="whether or not to skip registration",
    )
    result = parser.parse_args()

    # Create output directory
    print(f"Creating output directory: {result.outdir}")
    print(f"Creating output temp directory: {result.outdir}/tmp")
    gen_utils.utils.execute_cmd(f"mkdir -p {result.outdir} {result.outdir}/tmp")

    ndmg_dwi_worker(
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
        result.seeds,
        result.skipeddy,
        result.skipreg,
    )


if __name__ == "__main__":
    main()
