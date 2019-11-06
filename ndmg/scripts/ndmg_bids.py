#!/usr/bin/env python

"""
ndmg.scripts.ndmg_bids
~~~~~~~~~~~~~~~~~~~~~~

The top level ndmg entrypoint module.
In this module, ndmg:
1. Pulls data into the input directory from s3 if we need it.
2. Parses the input directory.
3. for each subject/session pair, runs ndmg_dwi_pipeline.ndmg_dwi_worker (the actual pipeline)
"""


# standard library imports
import sys
import glob
import os
from argparse import ArgumentParser
import subprocess
import warnings

# ndmg imports
from ndmg.utils import cloud_utils
from ndmg.utils.gen_utils import DirectorySweeper
from ndmg.utils.gen_utils import check_dependencies
from ndmg.utils.gen_utils import is_bids
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
    parcellations = [
        i for i in glob.glob(atlas_dir + "/atlases/label/Human/*.nii.gz") if dims in i
    ]
    parcellations = [os.path.join(atlas_dir, "label/Human/", l) for l in parcellations]

    assert all(map(os.path.exists, parcellations)), "Some parcellations do not exist."
    assert all(
        map(os.path.exists, [atlas, atlas_mask])
    ), "atlas or atlas_mask, does not exist. You may not have git-lfs -- if not, install it."
    return parcellations, atlas, atlas_mask


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

    return os.path.expanduser("~") + "/.ndmg/ndmg_atlases"  # local


def failure_message(subject, session, error):
    line = f"Subject {subject}, session {session} failed."
    line += f"Errror message: {error}"
    line += f"Trying next scan.\n"
    return line


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
        "--parcellation",
        action="store",
        help="The parcellation(s) being analyzed. Multiple parcellations can be provided with a space separated list.",
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

    # and ... begin!
    print("\nBeginning ndmg ...")

    # parse cli arguments
    result = parser.parse_args()
    inDir = result.bids_dir
    outDir = result.output_dir
    subjects = result.participant_label
    sessions = result.session_label
    parcellation_name = result.parcellation

    # arguments to be passed in every ndmg run
    kwargs = {
        "vox_size": result.vox,
        "mod_type": result.mod,
        "track_type": result.tt,
        "mod_func": result.mf,
        "seeds": result.seeds,
        "reg_style": result.sp,
        "clean": result.clean,
        "skipeddy": result.sked,
        "skipreg": result.skreg,
        "buck": result.bucket,
        "remo": result.remote_path,
        "push": result.push_data,
        "debug": result.debug,
        "modif": result.modif,
        "skull": result.skull,
    }

    # ---------------- Pre-run checks ---------------- #
    # make sure we have AFNI and FSL
    check_dependencies()

    # make sure input directory is BIDs-formatted
    is_bids_ = is_bids(inDir)
    assert is_bids_

    # check on input data

    # ---------------- Grab arguments --------------- #
    # Check to see if user has provided direction to an existing s3 bucket they wish to use
    try:
        creds = bool(cloud_utils.get_credentials())
    except:
        creds = bool(
            os.getenv("AWS_ACCESS_KEY_ID", 0) and os.getenv("AWS_SECRET_ACCESS_KEY", 0)
        )

    kwargs.update({"creds": creds})

    # TODO : `Flat is better than nested`. Make the logic for this cleaner.
    # this block of logic essentially just gets data we need from s3.
    # it's super gross.
    if kwargs["buck"] is not None and kwargs["remo"] is not None:
        if subjects is not None:
            # if len(sesh) == 1:
            #    sesh = sesh[0]
            for sub in subjects:
                if sessions is not None:
                    for ses in sessions:
                        rem = os.path.join(
                            kwargs["remo"], "sub-{}".format(sub), "ses-{}".format(ses)
                        )
                        tindir = os.path.join(
                            inDir, "sub-{}".format(sub), "ses-{}".format(ses)
                        )
                        cloud_utils.s3_get_data(
                            kwargs["buck"], rem, tindir, public=not creds
                        )
                else:
                    rem = os.path.join(kwargs["remo"], "sub-{}".format(sub))
                    tindir = os.path.join(inDir, "sub-{}".format(sub))
                    cloud_utils.s3_get_data(
                        kwargs["buck"], rem, tindir, public=not creds
                    )
        else:
            cloud_utils.s3_get_data(buck, kwargs["remo"], inDir, public=not creds)

    print("input directory contents: {}".format(os.listdir(inDir)))

    # get atlas stuff, then stick it into the kwargs
    atlas_dir = get_atlas_dir()
    parcellations, atlas, mask, = get_atlas(atlas_dir, kwargs["vox_size"])
    if parcellation_name is not None:  # filter parcellations
        parcellations = [file_ for file_ in parcellations if parcellation_name in file_]
    atlas_stuff = {"atlas": atlas, "mask": mask, "labels": parcellations}
    kwargs.update(atlas_stuff)

    # parse input directory
    sweeper = DirectorySweeper(inDir, subjects=subjects, sessions=sessions)
    scans = sweeper.get_dir_info()

    # ---------------- Run Pipeline --------------- #
    # run ndmg on the entire BIDs directory.
    # TODO: make sure this works on all scans
    for SubSesFile in scans:
        try:
            subject, session, files = SubSesFile
            current_outdir = f"{outDir}/sub-{subject}/ses-{session}"
            kwargs["outdir"] = current_outdir
            files.update(kwargs)
            ndmg_dwi_worker(**files)
        except Exception as error:
            failure = failure_message(subject, session, error)
            print(failure)
            continue


if __name__ == "__main__":
    main()
