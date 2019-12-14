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
from pathlib import Path

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
    parcellations,
    outdir,
    vox_size="2mm",
    mod_type="det",
    track_type="local",
    mod_func="csa",
    seeds=20,
    reg_style="native",
    skipeddy=False,
    skipreg=False,
    skull=None,
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
    parcellations : list
        Filepaths to the parcellations we're using.
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
    skull : str, optional
        skullstrip parameter pre-set. Default is "none".

    Raises
    ------
    ValueError
        Raised if downsampling voxel size is not supported
    ValueError
        Raised if bval/bvecs are potentially corrupted
    """

    # -------- Initial Setup ------------------ #
    # print starting arguments for clarity in log
    args = locals().copy()
    for arg, value in args.items():
        print(f"{arg} = {value}")

    # initial assertions
    if vox_size not in ["1mm", "2mm"]:
        raise ValueError("Voxel size not supported. Use 2mm or 1mm")

    print("Checking inputs...")
    for file_ in [t1w, bvals, bvecs, dwi, atlas, mask, *parcellations]:
        if not os.path.isfile(file_):
            raise FileNotFoundError(f"Input {file_} not found. Exiting ndmg.")
        else:
            print(f"Input {file_} found.")

    # time ndmg execution
    startTime = datetime.now()

    # initial variables
    outdir = Path(outdir)
    dwi_name = gen_utils.get_filename(dwi)

    # make output directory
    print("Adding directory tree...")
    parcellations = gen_utils.as_list(parcellations)
    gen_utils.make_initial_directories(outdir, parcellations=parcellations)

    # generate list of connectome file locations
    connectomes = []
    for parc in parcellations:
        name = gen_utils.get_filename(parc)
        folder = outdir / f"connectomes/{name}"
        connectome = f"{dwi_name}_{name}_connectome.csv"
        connectomes.append(str(folder / connectome))

    warm_welcome = welcome_message(connectomes)
    print(warm_welcome)

    # -------- Preprocessing Steps --------------------------------- #

    # set up directories
    prep_dwi: Path = outdir / "dwi/preproc"
    dwi_prep: Path = prep_dwi / "eddy_corrected_data.nii.gz"

    # check that skipping eddy correct is possible
    if skipeddy:
        # do it anyway if dwi_prep doesnt exist
        if not dwi_prep.is_file():
            print("Cannot skip preprocessing if it has not already been run!")
            skipeddy = False

    # if we're not skipping eddy correct, perform it
    if not skipeddy:
        prep_dwi = gen_utils.as_directory(prep_dwi, remove=True, return_as_path=True)
        preproc.eddy_correct(dwi, str(dwi_prep), 0)

    # copy bval/bvec files to output directory
    bvec_scaled = str(outdir / "dwi/preproc/bvec_scaled.bvec")
    fbval = str(outdir / "dwi/preproc/bval.bval")
    fbvec = str(outdir / "dwi/preproc/bvec.bvec")
    shutil.copyfile(bvecs, fbvec)
    shutil.copyfile(bvals, fbval)

    # Correct any corrupted bvecs/bvals
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    bvecs[np.where(np.any(abs(bvecs) >= 10, axis=1) == True)] = [1, 0, 0]
    bvecs[np.where(bvals == 0)] = 0
    bvecs_0_loc = np.all(abs(bvecs) == np.array([0, 0, 0]), axis=1)
    if len(bvecs[np.where(np.logical_and(bvals > 50, bvecs_0_loc))]) > 0:
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
    dwi_prep, bvecs = gen_utils.reorient_dwi(dwi_prep, bvec_scaled, prep_dwi)

    # Check dimensions
    dwi_prep = gen_utils.match_target_vox_res(dwi_prep, vox_size, outdir, sens="dwi")

    # Build gradient table
    print("fbval: ", fbval)
    print("bvecs: ", bvecs)
    print("fbvec: ", fbvec)
    print("dwi_prep: ", dwi_prep)
    gtab, nodif_B0, nodif_B0_mask = gen_utils.make_gtab_and_bmask(
        fbval, fbvec, dwi_prep, str(prep_dwi)
    )

    # Get B0 header and affine
    dwi_prep_img = nib.load(str(dwi_prep))
    hdr = dwi_prep_img.header

    # -------- Registration Steps ----------------------------------- #

    # define registration directory locations
    # TODO: possibly just pull these from a container generated by `gen_utils.make_initial_directories`
    reg_dirs = ["anat/preproc", "anat/registered", "tmp/reg_a", "tmp/reg_m"]
    reg_dirs = [outdir / loc for loc in reg_dirs]
    prep_anat, reg_anat, tmp_rega, tmp_regm = reg_dirs

    if not skipreg:
        for dir_ in [prep_anat, reg_anat]:
            if gen_utils.has_files(dir_):
                gen_utils.as_directory(dir_, remove=True)
        if gen_utils.has_files(tmp_rega) or gen_utils.has_files(tmp_regm):
            for tmp in [tmp_regm, tmp_rega]:
                gen_utils.as_directory(tmp, remove=True)

    # Check orientation (t1w)
    start_time = time.time()
    t1w = gen_utils.reorient_t1w(t1w, prep_anat)
    t1w = gen_utils.match_target_vox_res(t1w, vox_size, outdir, sens="anat")

    print("Running registration in native space...")

    # Instantiate registration
    reg = register.DmriReg(
        outdir, nodif_B0, nodif_B0_mask, t1w, vox_size, skull, simple=False
    )

    # Perform anatomical segmentation
    if skipreg and os.path.isfile(reg.wm_edge):
        print("Found existing gentissue run!")
    else:
        reg.gen_tissue()

    # Align t1w to dwi
    t1w2dwi_align_files = [reg.t1w2dwi, reg.mni2t1w_warp, reg.t1_aligned_mni]
    existing_files = all(map(os.path.isfile, t1w2dwi_align_files))
    if skipreg and existing_files:
        print("Found existing t1w2dwi run!")
    else:
        reg.t1w2dwi_align()

    # Align tissue classifiers
    tissue_align_files = [
        reg.wm_gm_int_in_dwi,
        reg.vent_csf_in_dwi,
        reg.corpuscallosum_dwi,
    ]
    existing_files = all(map(os.path.isfile, tissue_align_files))
    if skipreg and existing_files:
        print("Found existing tissue2dwi run!")
    else:
        reg.tissue2dwi_align()

    # Align atlas to dwi-space and check that the atlas hasn't lost any of the rois
    skullstrip_files = [reg, parcellations, prep_anat, vox_size, reg_style]
    labels_im_file_list = reg_utils.skullstrip_check(*skullstrip_files)
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
    trk_hdr = trct.make_hdr(streamlines, hdr)
    tractogram = nib.streamlines.Tractogram(
        streamlines, affine_to_rasmm=trk_hdr["voxel_to_rasmm"]
    )
    trkfile = nib.streamlines.trk.TrkFile(tractogram, header=trk_hdr)
    streams = os.path.join(namer["output"]["fiber"], "streamlines.trk")
    nib.streamlines.save(trkfile, streams)
    print("Streamlines complete")
    print(f"Tractography runtime: {np.round(time.time() - start_time, 1)}")

    if reg_style == "native_dsn":
        fa_path = track.tens_mod_fa_est(gtab, dwi_prep, nodif_B0_mask)
        # Normalize streamlines
        print("Running DSN...")
        streamlines_mni, streams_mni = register.direct_streamline_norm(
            streams, fa_path, namer
        )
        # Save streamlines to disk
        print("Saving DSN-registered streamlines: " + streams_mni)

    # ------- Connectome Estimation --------------------------------- #
    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(labels):
        print(f"Generating graph for {label} parcellation...")
        print(f"Applying native-space alignment to {labels[idx]}")
        if reg_style == "native":
            tracks = streamlines
        elif reg_style == "native_dsn":
            tracks = streamlines_mni
        rois = labels_im_file_list[idx]
        labels_im = nib.load(labels_im_file_list[idx])
        attr = len(np.unique(np.around(labels_im.get_data()).astype("int16"))) - 1
        g1 = graph.GraphTools(
            attr=attr,
            rois=rois,
            tracks=tracks,
            affine=np.eye(4),
            namer=namer,
            connectome_path=connectomes[idx],
        )
        g1.g = g1.make_graph()
        g1.summary()
        g1.save_graph_png(connectomes[idx])
        g1.save_graph(connectomes[idx])

    exe_time = datetime.now() - startTime

    print(f"Total execution time: {exe_time}")
    print("NDMG Complete.")
    print("~~~~~~~~~~~~~~\n\n")
    print(
        "NOTE :: you are using native-space registration to generate connectomes.\n Without post-hoc normalization, multiple connectomes generated with NDMG cannot be compared directly."
    )


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
    outdir_tmp = Path(result.outdir) / "tmp"
    outdir_tmp.mkdir(parents=True, exist_ok=True)

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
