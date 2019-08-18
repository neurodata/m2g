#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
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

# ndmg_bids.py
# Repackaged and maintained by Derek Pisner and Eric Bridgeford 2019
# Email: dpisner@utexas.edu
# Originally created by Greg Kiar on 2016-07-25.
# edited by Eric Bridgeford to incorporate fMRI, multi-threading, and
# skipeddy-graph generation.

import sys
import glob
import os.path as op
import warnings
from argparse import ArgumentParser
import subprocess

from ndmg.utils import s3_utils
from ndmg.utils.gen_utils import check_dependencies
from ndmg.utils.bids_utils import *
from ndmg.scripts.ndmg_dwi_pipeline import ndmg_dwi_worker

check_dependencies()
print("Beginning ndmg ...")

if os.path.isdir("/ndmg_atlases"):
    # in docker
    atlas_dir = "/ndmg_atlases"
else:
    # local
    atlas_dir = op.expanduser("~") + "/.ndmg/ndmg_atlases"

    # Data structure:
    # sub-<subject id>/
    #   ses-<session id>/
    #     anat/
    #       sub-<subject id>_ses-<session id>_T1w.nii.gz
    #     dwi/
    #       sub-<subject id>_ses-<session id>_dwi.nii.gz
    #   *   sub-<subject id>_ses-<session id>_dwi.bval
    #   *   sub-<subject id>_ses-<session id>_dwi.bvec
    #
    # *these files can be anywhere up stream of the dwi data, and are inherited.

    """
    Given the desired location for atlases and the type of processing, ensure
    we have all the atlases and parcellations.
    """


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
    if not op.exists(atlas_dir):
        # TODO : re-implement this pythonically with shutil and requests in python3.
        print("atlas directory not found. Cloning ...")
        clone = "https://github.com/neurodata/neuroparc.git"
        os.system("git lfs clone {} {}".format(clone, atlas_dir))

    atlas = op.join(
        atlas_dir, "atlases/reference_brains/MNI152NLin6_res-" + dims + "_T1w.nii.gz"
    )
    atlas_mask = op.join(
        atlas_dir,
        "atlases/mask/MNI152NLin6_res-" + dims + "_T1w_descr-brainmask.nii.gz",
    )
    labels = [
        i for i in glob.glob(atlas_dir + "/atlases/label/Human/*.nii.gz") if dims in i
    ]
    labels = [op.join(atlas_dir, "label/Human/", l) for l in labels]
    fils = labels + [atlas, atlas_mask]

    atlas_brain = None
    lv_mask = None

    assert all(map(os.path.exists, labels)), "Some parcellations do not exist."
    assert all(
        map(os.path.exists, [atlas, atlas_mask])
    ), "atlas or atlas_mask, does not exist. You may not have git-lfs -- if not, install it."
    return (labels, atlas, atlas_mask, atlas_brain, lv_mask)


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
    """

    labels, atlas, atlas_mask, atlas_brain, lv_mask = get_atlas(atlas_dir, vox_size)

    if atlas_select:
        labels = [i for i in labels if atlas_select in i]

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
    print(args)
    ndmg_dwi_worker(
        args[0][0],
        args[0][1],
        args[0][2],
        args[0][3],
        atlas,
        atlas_mask,
        labels,
        outDir,
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
        help="Voxel size to use for template registrations \
                        (e.g. default is '2mm')",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Whether or not to delete intemediates",
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
        help="Tracking approach: local or particle. Default is local.",
        default="local",
    )
    parser.add_argument(
        "--mf",
        action="store",
        help="Diffusion model: csd or csa. Default is csd.",
        default="csd",
    )
    parser.add_argument(
        "--sp",
        action="store",
        help="Space for tractography. Default is native.",
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

    # Check to see if user has provided direction to an existing s3 bucket they wish to use
    try:
        creds = bool(s3_utils.get_credentials())
    except:
        creds = bool(
            os.getenv("AWS_ACCESS_KEY_ID", 0) and os.getenv("AWS_SECRET_ACCESS_KEY", 0)
        )

    # TODO : `Flat is better than nested`. Make the logic for this cleaner.
    # this block of logic essentially just gets data we need from s3.
    # it's super gross.
    if buck is not None and remo is not None:
        if subj is not None:
            if len(sesh) == 1:
                sesh = sesh[0]
            for sub in subj:
                if sesh is not None:
                    remo = op.join(remo, "sub-{}".format(sub), "ses-{}".format(sesh))
                    tindir = op.join(inDir, "sub-{}".format(sub), "ses-{}".format(sesh))
                else:
                    remo = op.join(remo, "sub-{}".format(sub))
                    tindir = op.join(inDir, "sub-{}".format(sub))
                s3_utils.s3_get_data(buck, remo, tindir, public=not creds)
        else:
            s3_utils.s3_get_data(buck, remo, inDir, public=not creds)

    print("input directory contents: {}".format(os.listdir(inDir)))

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
    )


if __name__ == "__main__":
    main()
