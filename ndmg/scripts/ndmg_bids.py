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
from ndmg.utils import bids_s3
from ndmg.scripts.ndmg_pipeline import ndmg_pipeline
from ndmg.stats.qa_graphs import *
from ndmg.stats.qa_graphs_plotting import *

from glob import glob
import ndmg.utils as mgu
import ndmg
import os.path as op
import os
import sys


atlas_dir = '/ndmg_atlases'  # This location bc it is convenient for containers
atlas = op.join(atlas_dir, 'atlas/MNI152_T1_1mm.nii.gz')
atlas_mask = op.join(atlas_dir, 'atlas/MNI152_T1_1mm_brain_mask.nii.gz')
labels = ['labels/AAL.nii.gz',
          'labels/desikan.nii.gz',
          'labels/HarvardOxford.nii.gz',
          'labels/CPAC200.nii.gz',
          'labels/Talairach.nii.gz',
          'labels/JHU.nii.gz',
          'labels/slab907.nii.gz',
          'labels/slab1068.nii.gz',
          'labels/DS00071.nii.gz',
          'labels/DS00096.nii.gz',
          'labels/DS00108.nii.gz',
          'labels/DS00140.nii.gz',
          'labels/DS00195.nii.gz',
          'labels/DS00278.nii.gz',
          'labels/DS00350.nii.gz',
          'labels/DS00446.nii.gz',
          'labels/DS00583.nii.gz',
          'labels/DS00833.nii.gz',
          'labels/DS01216.nii.gz',
          'labels/DS01876.nii.gz',
          'labels/DS03231.nii.gz',
          'labels/DS06481.nii.gz',
          'labels/DS16784.nii.gz',
          'labels/DS72784.nii.gz']
labels = [op.join(atlas_dir, l) for l in labels]

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


def participant_level(inDir, outDir, subjs, sesh=None, debug=False):
    """
    Crawls the given BIDS organized directory for data pertaining to the given
    subject and session, and passes necessary files to ndmg_pipeline for
    processing.
    """
    # Get atlases
    ope = op.exists
    if any(not ope(l) for l in labels) or not (ope(atlas) and ope(atlas_mask)):
        print("Cannot find atlas information; downloading...")
        mgu().execute_cmd('mkdir -p ' + atlas_dir)
        cmd = " ".join(['wget -rnH --cut-dirs=3 --no-parent -P ' + atlas_dir,
                        'http://openconnecto.me/mrdata/share/atlases/'])
        mgu().execute_cmd(cmd)

    # Make output dir
    mgu().execute_cmd("mkdir -p " + outDir + " " + outDir + "/tmp")

    # Get subjects
    if subjs is None:
        subj_dirs = glob(op.join(inDir, "sub-*"))
        subjs = [subj_dir.split("-")[-1] for subj_dir in subj_dirs]

    bvec = []
    bval = []
    anat = []
    dwi = []
    # Get all image data for each subject
    for subj in subjs:
        if sesh is not None:
            anat_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                  "anat", "*_T1w.nii*"))
            dwi_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                 "dwi", "*_dwi.nii*"))
        else:
            anat_t = glob(op.join(inDir, "sub-%s" % subj, "anat",
                                  "*_T1w.nii*")) +\
                     glob(op.join(inDir, "sub-%s" % subj, "ses-*",
                                  "anat", "*_T1w.nii*"))
            dwi_t = glob(op.join(inDir, "sub-%s" % subj, "dwi",
                                 "*_dwi.nii*")) +\
                    glob(op.join(inDir, "sub-%s" % subj, "ses-*",
                                 "dwi", "*_dwi.nii*"))
        anat = anat + anat_t
        dwi = dwi + dwi_t

    bvec_t = []
    bval_t = []
    # Look for bval, bvec files for each DWI file
    for scan in dwi:
        step = op.dirname(scan)
        while not bval_t or not bvec_t:
            bval_t = glob(op.join(step, "*dwi.bval"))
            bvec_t = glob(op.join(step, "*dwi.bvec"))
            if step is op.abspath(op.join(inDir, os.pardir)):
                sys.exit("Error: No b-values or b-vectors found..\
                    \nPlease review BIDS spec (bids.neuroimaging.io).")
            step = op.abspath(op.join(step, os.pardir))
        bvec.append(bvec_t[0])
        bval.append(bval_t[0])
        bvec_t = []
        bval_t = []

    assert(len(anat) == len(dwi))
    assert(len(bvec) == len(dwi))
    assert(len(bval) == len(dwi))

    print(dwi)

    # Run for each
    for i, scans in enumerate(anat):
        print("T1 file: " + anat[i])
        print("DWI file: " + dwi[i])
        print("Bval file: " + bval[i])
        print("Bvec file: " + bvec[i])

        ndmg_pipeline(dwi[i], bval[i], bvec[i], anat[i], atlas, atlas_mask,
                      labels, outDir, clean=(not debug))


def group_level(inDir, outDir, dataset=None, atlas=None, minimal=False,
                log=False, hemispheres=False):
    """
    Crawls the output directory from ndmg and computes qc metrics on the
    derivatives produced
    """
    # Make output dir
    outDir += "/graphs"
    mgu().execute_cmd("mkdir -p " + outDir)

    # Get list of graphs
    labels = next(os.walk(inDir))[1]

    # Run for each
    if atlas is not None:
        labels = [atlas]

    for label in labels:
        print("Parcellation: " + label)
        tmp_in = op.join(inDir, label)
        fs = [op.join(tmp_in, fl)
              for root, dirs, files in os.walk(tmp_in)
              for fl in files
              if fl.endswith(".graphml") or fl.endswith(".gpickle")]
        tmp_out = op.join(outDir, label)
        mgu().execute_cmd("mkdir -p " + tmp_out)
        compute_metrics(fs, tmp_out, label)
        outf = op.join(tmp_out, 'plot')
        make_panel_plot(tmp_out, outf, dataset=dataset, atlas=label,
                        minimal=minimal, log=log, hemispheres=hemispheres)


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
                        choices=['participant', 'group'])
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
    minimal = result.minimal
    log = result.log
    atlas = result.atlas
    hemi = result.hemispheres

    creds = bool(os.getenv("AWS_ACCESS_KEY_ID", 0) and
                 os.getenv("AWS_SECRET_ACCESS_KEY", 0))

    if level == 'participant':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if subj is not None:
                [bids_s3.get_data(buck, remo, inDir, s, True) for s in subj]
            else:
                bids_s3.get_data(buck, remo, inDir, public=creds)
        modif = 'ndmg_{}'.format(ndmg.version.replace('.', '-'))
        participant_level(inDir, outDir, subj, sesh, result.debug)
    elif level == 'group':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if atlas is not None:
                bids_s3.get_data(buck, remo+'/graphs/'+atlas, inDir+'/'+atlas,
                                 public=creds)
            else:
                bids_s3.get_data(buck, remo+'/graphs', inDir, public=creds)
        modif = 'qa'
        group_level(inDir, outDir, result.dataset, result.atlas, minimal,
                    log, hemi)

    if push and buck is not None and remo is not None:
        print("Pushing results to S3...")
        cmd = "".join(['aws s3 cp --exclude "tmp/*" ', outDir, ' s3://', buck,
                       '/', remo, '/', modif,
                       '/ --recursive --acl public-read-write'])
        if not creds:
            print("Note: no credentials provided, may fail to push big files")
            cmd += ' --no-sign-request'
        print(cmd)
        mgu().execute_cmd(cmd)
    sys.exit(0)

if __name__ == "__main__":
    main()
