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
import traceback

# ndmg imports
from ndmg.utils import cloud_utils
from ndmg.utils.gen_utils import DirectorySweeper
from ndmg.utils.gen_utils import check_dependencies
from ndmg.utils.gen_utils import is_bids
from ndmg.utils.gen_utils import as_directory
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
        os.system(f"git lfs clone {clone} {atlas_dir}")

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


def failure_message(subject, session, tb):
    """
    Return a failure message.
    Called if a ndmg run fails.

    Parameters
    ----------
    subject : str
        Subject number.
    session : str
        Session number.
    tb : Error
        Error object containing the traceback text.

    Returns
    -------
    str
        Traceback with subject/session info
        to print to standard output.
    """
    error = ""
    tbexc = traceback.TracebackException(type(tb), tb, tb.__traceback__)
    # I have no idea what chain does, I found this on stackoverflow
    for line in tbexc.format(chain=True):
        error += line
    line = f"""
    Subject {subject}, session {session} failed. Error message:
    \n\n{error}
    Trying next scan.
    """
    return line


def main():
    """Starting point of the ndmg pipeline, assuming that you are using a BIDS organized dataset
    """

    parser = ArgumentParser(
        description="This is an end-to-end connectome estimation pipeline from M3r Images."
    )
    parser.add_argument(
        "input_dir",
        help="""The directory with the input dataset"
        formatted according to the BIDS standard.
        To use data from s3, just pass `s3://<bucket>/<dataset>` as the input directory.""",
    )
    parser.add_argument(
        "output_dir",
        help="""The local directory where the output
        files should be stored. If you are running group
        level analysis this folder should be prepopulated
        with the results of the participant level analysis.""",
    )
    parser.add_argument(
        "--participant_label",
        help="""The label(s) of the
        participant(s) that should be analyzed. The label
        corresponds to sub-<participant_label> from the BIDS
        spec (so it does not include "sub-"). If this
        parameter is not provided all subjects should be
        analyzed. Multiple participants can be specified
        with a space separated list.""",
        nargs="+",
    )
    parser.add_argument(
        "--session_label",
        help="""The label(s) of the
        session that should be analyzed. The label
        corresponds to ses-<participant_label> from the BIDS
        spec (so it does not include "ses-"). If this
        parameter is not provided all sessions should be
        analyzed. Multiple sessions can be specified
        with a space separated list.""",
        nargs="+",
    )
    #parser.add_argument(
    #    "--push_data",
    #    action="store_true",
    #    help="flag to push derivatives back up to S3.",
    #    default=False,
    #)
    parser.add_argument(
        "--push_location",
        action="store",
        help="Name of folder on s3 to push output data to, if the folder does not exist, it will be created."
        "Format the location as `s3://<bucket>/<path>`",
        default=None,
    )
    parser.add_argument(
        "--parcellation",
        action="store",
        help="The parcellation(s) being analyzed. Multiple parcellations can be provided with a space separated list.",
        default=None,
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
        "--voxelsize",
        action="store",
        default="2mm",
        help="Voxel size : 2mm, 1mm. Voxel size to use for template registrations.",
    )
    parser.add_argument(
        "--mod",
        action="store",
        help="Deterministic (det) or probabilistic (prob) tracking. Default is det.",
        default="det",
    )
    parser.add_argument(
        "--filtering_type",
        action="store",
        help="Tracking approach: local, particle. Default is local.",
        default="local",
    )
    parser.add_argument(
        "--diffusion_model",
        action="store",
        help="Diffusion model: csd, csa. Default is csa.",
        default="csa",
    )
    parser.add_argument(
        "--space",
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
        "--skull",
        action="store",
        help="""Special actions to take when skullstripping t1w image based on default skullstrip ('none') failure:
        Excess tissue below brain: below
        Chunks of cerebelum missing: cerebelum
        Frontal clipping near eyes: eye
        Excess clipping in general: general,""",
        default="none",
    )

    # and ... begin!
    print("\nBeginning ndmg ...")

    # ---------------- Parse CLI arguments ---------------- #
    result = parser.parse_args()
    inDir = result.input_dir
    outDir = result.output_dir
    subjects = result.participant_label
    sessions = result.session_label
    parcellation_name = result.parcellation

    # arguments to be passed in every ndmg run
    # TODO : change value naming convention to match key naming convention
    kwargs = {
        "vox_size": result.voxelsize,
        "mod_type": result.mod,
        "track_type": result.filtering_type,
        "mod_func": result.diffusion_model,
        "seeds": result.seeds,
        "reg_style": result.space,
        "skipeddy": result.sked,
        "skipreg": result.skreg,
        # "buck": result.bucket,
        # "remo": result.remote_path,
        # "push": result.push_data,
        "push": result.push_location, #modif
        "skull": result.skull,
    }

    # ---------------- S3 stuff ---------------- #
    # grab s3 stuff
    s3 = inDir.startswith("s3://")
    if s3:
        buck, remo = cloud_utils.parse_path(inDir)
        home = os.path.expanduser("~")
        inDir = as_directory(home + "/.ndmg/input", remove=True)
        #if kwargs["modif"]:
        #    kwargs["modif"].strip("/")
        creds = bool(cloud_utils.get_credentials())
        # TODO : Should we really prevent the pipeline from running in this case? What if user is pushing to a public bucket?
        if (not creds) and kwargs["push"]:
            raise AttributeError(
                """No AWS credentials found, but "--push_location" flag called. 
                Pushing will most likely fail."""
            )

        kwargs.update({"creds": creds})

        # Get S3 input data if needed
        # TODO : `Flat is better than nested`. Make the logic for this cleaner
        if subjects is not None:
            for subject in subjects:
                if sessions is not None:
                    for session in sessions:
                        info = f"sub-{subject}/ses-{session}"
                        cloud_utils.s3_get_data(buck, remo, inDir, info=info)
                else:
                    info = f"sub-{subject}"
                    cloud_utils.s3_get_data(buck, remo, inDir, info=info)
        else:
            info = "sub-"
            cloud_utils.s3_get_data(buck, remo, inDir, info=info)

    pd = kwargs["push"].startswith("s3://")
    if pd:
        buck, remo = cloud_utils.parse_path(kwargs["push"])
        kwargs["buck"] = buck
        remo.strip("/")
        kwargs["modif"] = remo.split("/")[-1]
        kwargs["remo"] = remo.replace(f'/{kwargs["modif"]}',"")
    kwargs["push"]=True


    # ---------------- Pre-run checks ---------------- #
    # check operating system compatibility
    compatible = sys.platform == "darwin" or sys.platform == "linux"
    if not compatible:
        input(
            "\n\nWARNING: You appear to be running ndmg on an operating system that is not macOS or Linux."
            "\nndmg has not been tested on this operating system and may not work. Press enter to continue.\n\n"
        )

    # make sure we have AFNI and FSL
    check_dependencies()
    # check on input data
    # make sure input directory is BIDs-formatted
    is_bids_ = is_bids(inDir)
    assert is_bids_

    print(
        f"""
        input directory location: {inDir}. 
        Input directory contents: {os.listdir(inDir)}.
        """
    )
    # ---------------- Grab parcellations, atlases, mask --------------- #
    # get parcellations, atlas, and mask, then stick it into kwargs
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
            kwargs["outdir"] = f"{outDir}/sub-{subject}/ses-{session}"
            files.update(kwargs)
            ndmg_dwi_worker(**files)
        except Exception as error:
            failure = failure_message(subject, session, error)
            print(failure)
            continue


if __name__ == "__main__":
    main()
