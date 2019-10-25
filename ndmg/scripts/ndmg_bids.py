#!/usr/bin/env python

"""
ndmg.scripts.ndmg_bids
~~~~~~~~~~~~~~~~~~~~~~

The top level ndmg entrypoint module.
In this module, ndmg:
1. Pulls input data from s3 if we need it.
2. Parses all input data.
3. for each set of input data, runs ndmg_dwi_pipeline.ndmg_dwi_worker (the actual pipeline)
"""


# standard library imports
import sys
import glob
import os
from argparse import ArgumentParser
import subprocess

# ndmg imports
from ndmg.utils import cloud_utils
from ndmg.utils.gen_utils import sweep_directory
from ndmg.utils.gen_utils import check_dependencies
from ndmg.utils.gen_utils import check_input_data
from ndmg.scripts.ndmg_dwi_pipeline import ndmg_dwi_worker


def get_atlas(atlas_dir, vox_size):
    """Given the desired location of atlases and the type of processing, ensure we have all the atlases and parcellations.

    Parameters
    ----------
    atlas_dir : str
        Path to directory containing atlases.
    vox_size : str
        t1w input image voxel dimensions, either 2mm or 1mm

    Returns
    -------
    tuple
        filepaths corresponding to the human parcellations, the atlas, and the atlas's mask. atals_brain and lv_mask is None if not fmri.

    Raises
    ------
    ValueError
        raised if dimensionality is wrong.
    NotImplementedError
        currently raised in lieu of atlas pulling capabilities.
    """
    if vox_size == "2mm":
        dims = "2x2x2"
    elif vox_size == "1mm":
        dims = "1x1x1"
    else:
        raise ValueError(
            "Voxel dimensions of input t1w image not currently supported by ndmg."
        )

    # grab atlases if they don't exist
    if not os.path.exists(atlas_dir):
        # TODO : re-implement this pythonically with shutil and requests in python3.
        print("atlas directory not found. Cloning ...")
        clone = "https://github.com/neurodata/neuroparc.git"
        os.system("git lfs clone {} {}".format(clone, atlas_dir))

    atlas = os.path.join(
        atlas_dir, "atlases/reference_brains/MNI152NLin6_res-" + dims + "_T1w.nii.gz"
    )
    atlas_mask = os.path.join(
        atlas_dir,
        "atlases/mask/MNI152NLin6_res-" + dims + "_T1w_descr-brainmask.nii.gz",
    )
    labels = [
        i for i in glob.glob(atlas_dir + "/atlases/label/Human/*.nii.gz") if dims in i
    ]
    labels = [os.path.join(atlas_dir, "label/Human/", l) for l in labels]
    fils = labels + [atlas, atlas_mask]

    atlas_brain = None
    lv_mask = None

    assert all(map(os.path.exists, labels)), "Some parcellations do not exist."
    assert all(
        map(os.path.exists, [atlas, atlas_mask])
    ), "atlas or atlas_mask, does not exist. You may not have git-lfs -- if not, install it."
    return (labels, atlas, atlas_mask, atlas_brain, lv_mask)


def get_atlas_dir():
    """
    Gets the location of ndmg's atlases.
    
    Returns
    -------
    str
        atlas directory location.
    """
    if os.path.isdir("/ndmg_atlases"):
        return "/ndmg_atlases"  # in docker
    else:
        return os.path.expanduser("~") + "/.ndmg/ndmg_atlases"  # local


def session_level(
    inDir,
    outDir,
    subjs,
    vox_size,
    skipeddy,
    skipreg,
    clean,
    atlas_select,
    mod_type,
    track_type,
    mod_func,
    seeds,
    reg_style,
    sesh=None,
    run=None,
    buck=None,
    remo=None,
    push=False,
    creds=None,
    debug=False,
    modif="",
    skull="none",
):
    """Crawls the given BIDS organized directory for data pertaining to the given subject and session, and passes necessary files to ndmg_dwi_pipeline for processing.

    Parameters
    ----------
    inDir : str
        Path to BIDS input directory
    outDir : str
        Path to output directory
    subjs : list
        subject label
    vox_size : str
        Voxel size to use for template registrations.
    skipeddy : bool
        Whether to skip eddy correction if it has already been run. False means don't.
    skipreg : bool
        Whether to skip registration if it has already been run. False means don't.
    clean : bool
        Whether or not to delete intermediates
    atlas_select : str
        The atlas being analyzed in QC (if you only want one)
    mod_type : str
        Determinstic (det) or probabilistic (prob) tracking
    track_type : str
        Tracking approach: eudx or local. Default is eudx
    mod_func : str
        Which diffusion model you want to use, csd or csa
    reg_style : str
        Space for tractography.
    sesh : str, optional
        The label of the session that should be analyzed. If not provided all sessions are analyzed. Multiple sessions can be specified with a space separated list. Default is None
    task : str, optional
        task label. Default is None
    run : str, optional
        run label. Default is None
    buck : str, optional
        The name of an S3 bucket which holds BIDS organized data. You musht have build your bucket with credentials to the S3 bucket you wish to access. Default is None
    remo : str, optional
        The path to the data on your S3 bucket. The data will be downloaded to the provided bids_dir on your machine. Default is None.
    push : bool, optional
        Flag to push derivatives back to S3. Default is False
    creds : bool, optional
        Determine if you have S3 credentials. Default is None
    debug : bool, optional
        If False, remove any old filed in the output directory. Default is False
    modif : str, optional
        Name of the folder on s3 to push to. If empty, push to a folder with ndmg's version number. Default is ""
    skull : str, optional
        Additional skullstrip analysis parameter set for unique t1w images. Default is "none".
    """

    # get atlas directory
    atlas_dir = get_atlas_dir()

    # parse atlas directory
    labels, atlas, atlas_mask, atlas_brain, lv_mask = get_atlas(atlas_dir, vox_size)

    if atlas_select:
        labels = [i for i in labels if atlas_select in i]

    # parse input directory
    result = sweep_directory(inDir, subjs, sesh, run)

    dwis, bvals, bvecs, anats = result
    assert len(anats) == len(dwis)
    assert len(bvecs) == len(dwis)
    assert len(bvals) == len(dwis)
    args = [
        [
            dw,
            bval,
            bvec,
            anat,
            atlas,
            atlas_mask,
            labels,
            "%s%s%s%s%s"
            % (
                outDir,
                "/sub",
                bval.split("sub")[1].split("/")[0],
                "/ses",
                bval.split("ses")[1].split("/")[0],
            ),
        ]
        for (dw, bval, bvec, anat) in zip(dwis, bvals, bvecs, anats)
    ]

    # optional args stored in kwargs
    # use worker wrapper to call function f with args arg
    # and keyword args kwargs
    for arg in args:
        ndmg_dwi_worker(
            arg[0],
            arg[1],
            arg[2],
            arg[3],
            atlas,
            atlas_mask,
            labels,
            arg[7],
            vox_size,
            mod_type,
            track_type,
            mod_func,
            seeds,
            reg_style,
            clean,
            skipeddy,
            skipreg,
            buck=buck,
            remo=remo,
            push=push,
            creds=creds,
            debug=debug,
            modif=modif,
            skull=skull,
        )
    rmflds = []
    if len(rmflds) > 0:
        cmd = "rm -rf {}".format(" ".join(rmflds))
        mgu.execute_cmd(cmd)
    sys.exit(0)  # terminated


def main():
    """Starting point of the ndmg pipeline, assuming that you are using a BIDS organized dataset
    """
    parser = ArgumentParser(
        description="This is an end-to-end connectome estimation pipeline from M3r Images."
    )
    parser.add_argument(
        "bids_dir",
        help="The directory with the input dataset"
        " formatted according to the BIDS standard.",
    )
    parser.add_argument(
        "output_dir",
        help="The directory where the output "
        "files should be stored. If you are running group "
        "level analysis this folder should be prepopulated "
        "with the results of the participant level analysis.",
    )
    parser.add_argument(
        "--participant_label",
        help="The label(s) of the "
        "participant(s) that should be analyzed. The label "
        "corresponds to sub-<participant_label> from the BIDS "
        'spec (so it does not include "sub-"). If this '
        "parameter is not provided all subjects should be "
        "analyzed. Multiple participants can be specified "
        "with a space separated list.",
        nargs="+",
    )
    parser.add_argument(
        "--session_label",
        help="The label(s) of the "
        "session that should be analyzed. The label "
        "corresponds to ses-<participant_label> from the BIDS "
        'spec (so it does not include "ses-"). If this '
        "parameter is not provided all sessions should be "
        "analyzed. Multiple sessions can be specified "
        "with a space separated list.",
        nargs="+",
    )
    parser.add_argument(
        "--run_label",
        help="The label(s) of the run "
        "that should be analyzed. The label corresponds to "
        "run-<run_label> from the BIDS spec (so it does not "
        'include "task-"). If this parameter is not provided '
        "all runs should be analyzed. Multiple runs can be "
        "specified with a space separated list.",
        nargs="+",
    )
    parser.add_argument(
        "--bucket",
        action="store",
        help="The name of "
        "an S3 bucket which holds BIDS organized data. You "
        "must have built your bucket with credentials to the "
        "S3 bucket you wish to access.",
    )
    parser.add_argument(
        "--remote_path",
        action="store",
        help="The path to "
        "the data on your S3 bucket. The data will be "
        "downloaded to the provided bids_dir on your machine.",
    )
    parser.add_argument(
        "--push_data",
        action="store_true",
        help="flag to " "push derivatives back up to S3.",
        default=False,
    )
    parser.add_argument(
        "--dataset",
        action="store",
        help="The name of " "the dataset you are perfoming QC on.",
    )
    parser.add_argument(
        "--atlas",
        action="store",
        help="The atlas " "being analyzed in QC (if you only want one).",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="If False, remove any old files in the output directory.",
        default=False,
    )
    parser.add_argument(
        "--sked",
        action="store_true",
        help="Whether to skip eddy correction if it has already been run.",
        default=False,
    )
    parser.add_argument(
        "--skreg",
        action="store_true",
        default=False,
        help="whether or not to skip registration",
    )
    parser.add_argument(
        "--vox",
        action="store",
        default="2mm",
        help="Voxel size : 2mm, 1mm. Voxel size to use for template registrations.gi",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Whether or not to delete intermediates",
    )
    parser.add_argument(
        "--mod",
        action="store",
        help="Determinstic (det), probabilistic (prob) tracking. Default is det.",
        default="det",
    )
    parser.add_argument(
        "--tt",
        action="store",
        help="Tracking approach: local, particle. Default is local.",
        default="local",
    )
    parser.add_argument(
        "--mf",
        action="store",
        help="Diffusion model: csd, csa. Default is csa.",
        default="csa",
    )
    parser.add_argument(
        "--sp",
        action="store",
        # help="Space for tractography: mni, native_dsn, native. Default is native.",
        help="Space for tractography: native, native_dsn. Default is native.",
        default="native",
    )
    parser.add_argument(
        "--seeds",
        action="store",
        help="Seeding density for tractography. Default is 20.",
        default=20,
    )
    parser.add_argument(
        "--modif",
        action="store",
        help="Name of folder on s3 to push to. If empty, push to a folder with ndmg's version number.",
        default="",
    )
    parser.add_argument(
        "--skull",
        action="store",
        help="Special actions to take when skullstripping t1w image based on default skullstrip ('none') failure:"
        "Excess tissue below brain: below"
        "Chunks of cerebelum missing: cerebelum"
        "Frontal clipping near eyes: eye"
        "Excess clipping in general: general",
        default="none",
    )

    # parse cli arguments
    result = parser.parse_args()
    inDir = result.bids_dir
    outDir = result.output_dir
    subj = result.participant_label
    sesh = result.session_label
    run = result.run_label
    buck = result.bucket
    remo = result.remote_path
    push = result.push_data
    debug = result.debug
    seeds = result.seeds
    skipeddy = result.sked
    skipreg = result.skreg
    clean = result.clean
    vox_size = result.vox
    atlas_select = result.atlas
    mod_type = result.mod
    track_type = result.tt
    mod_func = result.mf
    reg_style = result.sp
    modif = result.modif
    skull = result.skull

    # initial setup and checks
    print("Beginning ndmg ...")
    check_dependencies()
    check_input_data(inDir)

    # Check to see if user has provided direction to an existing s3 bucket they wish to use
    try:
        creds = bool(cloud_utils.get_credentials())
    except:
        creds = bool(
            os.getenv("AWS_ACCESS_KEY_ID", 0) and os.getenv("AWS_SECRET_ACCESS_KEY", 0)
        )

    # TODO : `Flat is better than nested`. Make the logic for this cleaner.
    # this block of logic essentially just gets data we need from s3.
    # it's super gross.
    if buck is not None and remo is not None:
        if subj is not None:
            # if len(sesh) == 1:
            #    sesh = sesh[0]
            for sub in subj:
                if sesh is not None:
                    for ses in sesh:
                        rem = os.path.join(
                            remo, "sub-{}".format(sub), "ses-{}".format(ses)
                        )
                        tindir = os.path.join(
                            inDir, "sub-{}".format(sub), "ses-{}".format(ses)
                        )
                        cloud_utils.s3_get_data(buck, rem, tindir, public=not creds)
                else:
                    rem = os.path.join(remo, "sub-{}".format(sub))
                    tindir = os.path.join(inDir, "sub-{}".format(sub))
                    cloud_utils.s3_get_data(buck, rem, tindir, public=not creds)
        else:
            cloud_utils.s3_get_data(buck, remo, inDir, public=not creds)

    print("input directory contents: {}".format(os.listdir(inDir)))

    # run session-level ndmg
    session_level(
        inDir,
        outDir,
        subj,
        vox_size,
        skipeddy,
        skipreg,
        clean,
        atlas_select,
        mod_type,
        track_type,
        mod_func,
        seeds,
        reg_style,
        sesh,
        run,
        buck=buck,
        remo=remo,
        push=push,
        creds=creds,
        debug=debug,
        modif=modif,
        skull=skull,
    )


if __name__ == "__main__":
    main()
