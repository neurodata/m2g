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
# bids.py
# Created by Greg Kiar on 2016-07-29.
# Email: gkiar@jhu.edu
# Edited by Eric Bridgeford.

import ndmg.utils as mgu
import os.path as op
import os
import sys
import boto3
from glob import glob
import re


def match_anatomical(inDir, subj, anat_opt, modal):
    """
    A function to match from a list of anatomical scans to a corresponding
    modality specific scan.

    **Positional Arguments:**
        - inDir:
            - the base directory for inputs.
        - subj:
            - the current subject.
        - anat_opt:
            - a list of possible anatomical scans. Note that the list
              is expected to have at least 1 element.
        - modal:
            - a modality specific scan that we want to find a corresponding
              anatomical match for.
    """
    match_ses = op.join(inDir, "sub-{}/ses-([\s\S]*?)".format(subj))
    # see if we have a session-level modality file
    session_match = re.search(match_ses, modal)
    if session_match is not None:
        # try to find an associated anatomical scan from that same session
        match = [s for s in anat_opt if session_match.group(0) in s]
        if len(match) > 0:
            # return the anatomical scan from this particular session
            return match[0]
    # if we do not meet any more detailed matches, just return the most basic
    # subject-level match
    return anat_opt[0]


def crawl_bids_directory(inDir, subjs, sesh, dwi=True):
    """
    Given a BIDS directory and optionally list of sessions and subjects,
    crawls the path and returns pointers to all relevant files for analysis.
    """
    if subjs is None:
        subj_dirs = glob(op.join(inDir, "sub-*"))
        subjs = [subj_dir.split("-")[-1] for subj_dir in subj_dirs]

    mod = []
    anat = []

    if dwi:
        modality='dwi'
        modal_str = "dwi"
    else:
        modality='func'
        modal_str = "bold"

    for subj in subjs:
        if sesh is not None:
            mod_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                 modality, "*{}.nii*".format(modal_str)))
            anat_opt = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                    "anat", "*_T1w.nii*"))
        else:
            mod_t = glob(op.join(inDir, "sub-{}".format(subj), modality,
                                 "*_{}.nii*".format(modal_str))) +\
                    glob(op.join(inDir, "sub-{}".format(subj), "ses-*",
                                 modality, "*_{}.nii*".format(modal_str)))
            # options for anatomical scans
            anat_opt = glob(op.join(inDir, "sub-{}".format(subj), "anat",
                                    "*_T1w.nii*")) +\
                       glob(op.join(inDir, "sub-{}".format(subj), "ses-*",
                                    "anat", "*_T1w.nii*"))
        # if we are missing anatomical or modality-specific scans, we cannot
        # analyze this subject.
        if len(anat_opt) > 0 and len(mod_t) > 0:
            anat_t = []
            for modal in mod_t:
                anat_match = match_anatomical(inDir, subj, anat_opt, modal)
                anat_t.append(anat_match)
            mod = mod + mod_t
            anat = anat + anat_t

    if modality == "func":
        return(anat, mod)

    bvec_t = []
    bval_t = []
    # Look for bval, bvec files for each DWI file
    for scan in mod:
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
    return (anat, mod, bvec, bval)


def s3_get_data(bucket, remote, local, public=True):
    """
    Given an s3 bucket, data location on the bucket, and a download location,
    crawls the bucket and recursively pulls all data.
    """
    client = boto3.client('s3')
    if not public:
        bkts = [bk['Name'] for bk in client.list_buckets()['Buckets']]
        if bucket not in bkts:
            sys.exit("Error: could not locate bucket. Available buckets: " +
                     ", ".join(bkts))

    cmd = 'aws s3 cp --recursive s3://{}/{}/ {}'.format(bucket, remote, local)
    if public:
        cmd += ' --no-sign-request --region=us-east-1'

    std, err = mgu.execute_cmd('mkdir -p {}'.format(local))
    std, err = mgu.execute_cmd(cmd)


def s3_push_data(bucket, remote, outDir, modifier, creds=True):
        cmd = 'aws s3 cp --exclude "tmp/*" {} s3://{}/{}/{} --recursive --acl public-read'
        cmd = cmd.format(outDir, bucket, remote, modifier)
        if not creds:
            print("Note: no credentials provided, may fail to push big files.")
            cmd += ' --no-sign-request'
        mgu.execute_cmd(cmd)
