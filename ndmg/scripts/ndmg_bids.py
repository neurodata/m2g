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
# Created by Greg Kiar on 2016-07-25.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
from subprocess import Popen, PIPE
from os.path import expanduser
from ndmg.scripts.ndmg_setup import get_files
from ndmg.scripts.ndmg_dwi_pipeline import ndmg_dwi_pipeline
from ndmg.utils.bids import *
from ndmg.stats.qa_graphs import *
from ndmg.stats.qa_graphs_plotting import *
from glob import glob
import ndmg.utils as mgu
import ndmg
import os.path as op
import os
import sys


atlas_dir = '/ndmg_atlases'  # This location bc it is convenient for containers

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

skippers = ['slab907', 'slab1068', 'DS01216', 'DS01876',
            'DS03231', 'DS06481', 'DS16784', 'DS72784']

def get_atlas(atlas_dir, dwi=True):
    """
    Given the desired location for atlases and the type of processing, ensure
    we have all the atlases and parcellations.
    """
    if dwi:
        atlas = op.join(atlas_dir, 'atlas/MNI152_T1_1mm.nii.gz')
        atlas_mask = op.join(atlas_dir, 'atlas/MNI152_T1_1mm_brain_mask.nii.gz')
        labels = ['labels/AAL.nii.gz', 'labels/desikan.nii.gz',
                  'labels/Desikan2012.nii.gz',
                  'labels/HarvardOxford.nii.gz', 'labels/CPAC200.nii.gz',
                  'labels/Talairach.nii.gz', 'labels/JHU.nii.gz',
                  'labels/slab907.nii.gz', 'labels/slab1068.nii.gz',
                  'labels/DS00071.nii.gz', 'labels/DS00096.nii.gz',
                  'labels/DS00108.nii.gz', 'labels/DS00140.nii.gz',
                  'labels/DS00195.nii.gz', 'labels/DS00278.nii.gz',
                  'labels/DS00350.nii.gz', 'labels/DS00446.nii.gz',
                  'labels/DS00583.nii.gz', 'labels/DS00833.nii.gz',
                  'labels/DS01216.nii.gz', 'labels/DS01876.nii.gz',
                  'labels/DS03231.nii.gz', 'labels/DS06481.nii.gz',
                  'labels/DS16784.nii.gz', 'labels/DS72784.nii.gz']
        labels = [op.join(atlas_dir, l) for l in labels]
        fils = labels + [atlas, atlas_mask]
    else:
        atlas = atlas_dir + '/atlas/MNI152_T1-2mm.nii.gz'
        atlas_brain = atlas_dir + '/atlas/MNI152_T1-2mm_brain.nii.gz'
        atlas_mask = atlas_dir + '/atlas/MNI152_T1-2mm_brain_mask.nii.gz'
        lv_mask = atlas_dir + '/atlas/HarvOx_lv_thr25-2mm.nii.gz'
        labels = ['/labels/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz',
                  '/labels/aal-2mm.nii.gz', '/labels/brodmann-2mm.nii.gz',
                  '/labels/desikan-2mm.nii.gz', '/labels/Talairach-2mm.nii.gz']
        labels = [op.join(atlas_dir, l) for l in labels]
        fils = labels + [atlas, atlas_mask, atlas_brain, lv_mask]

    ope = op.exists
    if any(not ope(f) for f in fils):
        print("Cannot find atlas information; please download and unzip as follows...")
        print("Source: s3://mrneurodata/data/resources/ndmg_atlases.zip")
        print("Destination: {}".format(atlas_dir))

    if dwi:
        atlas_brain = None
        lv_mask = None
    return (labels, atlas, atlas_mask, atlas_brain, lv_mask)


def session_level(inDir, outDir, subjs, sesh=None, debug=False,
                      stc=None, dwi=True):
    """
    Crawls the given BIDS organized directory for data pertaining to the given
    subject and session, and passes necessary files to ndmg_pipeline for
    processing.
    """
    labels, atlas, atlas_mask, atlas_brain, lv_maks = get_atlas(atlas_dir, dwi)

    mgu.execute_cmd("mkdir -p {} {}/tmp".format(outDir, outDir))

    anat, func, dwi, bvec, bval = crawl_bids_directory(inDir, subjs, sesh)
    
    if dwi:
        assert(len(anat) == len(dwi))
        assert(len(bvec) == len(dwi))
        assert(len(bval) == len(dwi))
    else:
        assert(len(anat) == len(func))

    for i, scans in enumerate(anat):
        print("T1 file: {}".format(anat[i]))
        if dwi:
            print("DWI file: {}".format(dwi[i]))
            print("Bval file: {}".format(bval[i]))
            print("Bvec file: {}".format(bvec[i]))

            ndmg_dwi_pipeline(dwi[i], bval[i], bvec[i], anat[i], atlas,
                              atlas_mask, labels, outDir, clean=(not debug))


def group_level(inDir, outDir, dataset=None, atlas=None, minimal=False,
                log=False, hemispheres=False, dwi=True):
    """
    Crawls the output directory from ndmg and computes qc metrics on the
    derivatives produced
    """
    if not dwi:
        print("Currently there is no group level analysis for fmri.")
        return -1

    outDir = op.join(outDir, 'qa', 'graphs')
    mgu.execute_cmd("mkdir -p {}".format(outDir))

    labels_used = next(os.walk(inDir))[1]

    if atlas is not None:
        labels_used = [atlas]

    for skip in skippers:
        if skip in labels_used:
            print("Skipping {} parcellation".format(skip))
            labels_used.remove(skip)
            continue

    for label in labels_used:
        print("Parcellation: {}".format(label))
        tmp_in = op.join(inDir, label)
        fs = [op.join(tmp_in, fl)
              for root, dirs, files in os.walk(tmp_in)
              for fl in files
              if fl.endswith(".graphml") or fl.endswith(".gpickle")]
        tmp_out = op.join(outDir, label)
        mgu.execute_cmd("mkdir -p {}".format(tmp_out))
        try:
            compute_metrics(fs, tmp_out, label)
            outf = op.join(tmp_out, '{}_plot'.format(label))
            make_panel_plot(tmp_out, outf, dataset=dataset, atlas=label,
                            minimal=minimal, log=log, hemispheres=hemispheres)
        except:
            print("Failed group analysis for {} parcellation.".format(label))
            print("-- graphs contain isolates")
            continue


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")

    parser.add_argument('bids_dir', help='The directory with the input dataset'
                        ' formatted according to the BIDS standard.')
    parser.add_argument('output_dir', help='The directory where the output '
                        'files should be stored. If you are running group '
                        'level analysis this folder should be prepopulated '
                        'with the results of the participant level analysis.')
    parser.add_argument('analysis_level', help='Level of the analysis that '
                        'will be performed. Multiple participant level '
                        'analyses can be run independently (in parallel) '
                        'using the same output_dir.',
                        choices=['session', 'group'])
    parser.add_argument('--participant_label', help='The label(s) of the '
                        'participant(s) that should be analyzed. The label '
                        'corresponds to sub-<participant_label> from the BIDS '
                        'spec (so it does not include "sub-"). If this '
                        'parameter is not provided all subjects should be '
                        'analyzed. Multiple participants can be specified '
                        'with a space separated list.', nargs="+")
    parser.add_argument('--session_label', help='The label(s) of the '
                        'session that should be analyzed. The label '
                        'corresponds to ses-<participant_label> from the BIDS '
                        'spec (so it does not include "ses-"). If this '
                        'parameter is not provided all sessions should be '
                        'analyzed. Multiple sessions can be specified '
                        'with a space separated list.')
    parser.add_argument('--bucket', action='store', help='The name of '
                        'an S3 bucket which holds BIDS organized data. You '
                        'must have built your bucket with credentials to the '
                        'S3 bucket you wish to access.')
    parser.add_argument('--remote_path', action='store', help='The path to '
                        'the data on your S3 bucket. The data will be '
                        'downloaded to the provided bids_dir on your machine.')
    parser.add_argument('--push_data', action='store_true', help='flag to '
                        'push derivatives back up to S3.', default=False)
    parser.add_argument('--dataset', action='store', help='The name of '
                        'the dataset you are perfoming QC on.')
    parser.add_argument('--atlas', action='store', help='The atlas '
                        'being analyzed in QC (if you only want one).')
    parser.add_argument('--minimal', action='store_true', help='Determines '
                        'whether to show a minimal or full set of plots.',
                        default=False)
    parser.add_argument('--hemispheres', action='store_true', help='Whether '
                        'or not to break degrees into hemispheres or not',
                        default=False)
    parser.add_argument('--log', action='store_true', help='Determines '
                        'axis scale for plotting.', default=False)
    parser.add_argument('--debug', action='store_true', help='flag to store '
                        'temp files along the path of processing.',
                        default=False)
    result = parser.parse_args()

    inDir = result.bids_dir
    outDir = result.output_dir
    subj = result.participant_label
    sesh = result.session_label
    buck = result.bucket
    remo = result.remote_path
    push = result.push_data
    level = result.analysis_level
    debug = result.debug
    
    minimal = result.minimal
    log = result.log
    atlas = result.atlas
    dataset = result.dataset
    hemi = result.hemispheres

    creds = bool(os.getenv("AWS_ACCESS_KEY_ID", 0) and
                 os.getenv("AWS_SECRET_ACCESS_KEY", 0))

    if level == 'session':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if subj is not None:
                for sub in subj:
                    if sesh is not None:
                        tpath = op.join(remo, 'sub-{}'.format(sub), 'ses-{}'.format(sesh))
                        tindir = op.join(inDir, 'sub-{}'.format(sub), 'ses-{}'.format(sesh))
                    else:
                        tpath = op.join(remo, 'sub-{}'.format(sub))
                        tindir = op.join(inDir, 'sub-{}'.format(sub))
                s3_get_data(buck, tpath, tindir, public=creds)
            else: 
                s3_get_data(buck, remo, inDir, public=creds)
        modif = 'ndmg'
        session_level(inDir, outDir, subj, sesh, debug)

    elif level == 'group':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if atlas is not None:
                tpath = op.join(remo, 'graphs', atlas)
                tindir = op.join(outDir, 'graphs', atlas)
                # Using outDir as input location for group level since i work on graphs
            else:
                tpath = op.join(remo, 'graphs')
                tindir = op.join(outDir, 'graphs')
            s3_get_data(buck, tpath, tindir, public=creds)
        modif = 'qa'
        group_level(op.join(outDir, 'graphs'), outDir, dataset, atlas, minimal, log, hemi)

    if push and buck is not None and remo is not None:
        print("Pushing results to S3...")
        s3_push_data(buck, remo, outDir, modif, creds)


if __name__ == "__main__":
    main()

