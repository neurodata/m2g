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
import fnmatch

def match_t1w(epi, t1ws, modality):
    """
    A function to match an epi scan to a t1w scan, given a list of t1w scans
    for a particular subject.

    **Positional Arguments:**

        - epi:
            - the epi scan to match a t1w to.
        - t1ws:
            - a list of all the t1w scans for a particular subject to choose
              from.
        - modality:
            - the modality identifier for the epi scan. Can be 'func' or 'dwi'.
    """
    # look for a session label
    ses = re.search('(?<=ses-)(.*)(?=/{})'.format(modality), epi)
    # if we have a session label, look for a T1w that uses this label
    # the directory structure for this situation would be:
    # sub-##/
    #    + ses-###/
    #        + anat/
    #        + func/
    #        + dwi/
    #    + ses-####/
    #    ...
    # ...
    if ses is not None:
        ses = ses.group(0)
        # if our t1w contains this session's label, then it is a match
        matches = [t1w for t1w in t1ws if 'ses-{}'.format(ses) in t1w]
        # if we have multiple t1ws for a given session, just use the first
        # one
        if len(matches) > 0:
            return matches[0]

    # if we do not have a session label, then just return the first
    # t1w we have, since our collection of t1ws are all the t1ws for a subject
    # the directory structure for this would be:
    # sub-##/
    #    + anat/
    #    + func/
    #    + dwi/
    # ...
    if len(t1ws) > 0:
        return t1ws[0]
    else:
        sys.exit('Error: No t1w scan associated with subject: '
                 + epi + '. Please review BIDs spec (bids.neurodata.io).')


def get_files(inDir, subj, modality):
    """
    A function that uses os.walk to find all of the nifti images
    associated with a particular subject, given a particular modality
    identifier according to BIDs spec.

    **Positional Arguments:**
        - inDir:
            - the BIDs directory to check for files.
        - subj:
            - the subject identifier.
        - modality:
            - the modality identifier. Can be T1w, bold, or dwi.
    """
    matches_epi = []
    matches_t1w = []
    subdir = op.join(inDir, 'sub-{}'.format(subj))
    for root, dirnames, filenames in os.walk(subdir):
        fstr = '*{}.nii*'.format(modality)
        for filename in fnmatch.filter(filenames, fstr):
            matches_epi.append(os.path.join(root, filename))
        ft1w = '*T1w.nii*'
        for filename in fnmatch.filter(filenames, ft1w):
            matches_t1w.append(os.path.join(root, filename))
    return matches_epi, matches_t1w


def crawl_bids_directory(inDir, subjs, sesh, dwi=True):
    """
    Given a BIDS directory and optionally list of sessions and subjects,
    crawls the path and returns pointers to all relevant files for analysis.
    """
    if subjs is None:
        subj_dirs = glob(op.join(inDir, "sub-*"))
        subjs = [subj_dir.split("-")[-1] for subj_dir in subj_dirs]

    epis = []
    t1ws = []
    if dwi:
        modality='dwi'
        modal_str = "dwi"
    else:
        modality='func'
        modal_str = "bold"

    for subj in subjs:
        # collect all the epis for a given subject
        # collect the epis and t1ws for a given subject
        (epis_sub, t1ws_sub) = get_files(inDir, subj, modal_str)
        # for each epi, find the best-match anatomical scan
        t1w_match = [match_t1w(epi, t1ws_sub, modality) for epi in epis_sub]
        epis = epis + epis_sub
        t1ws = t1ws + t1w_match

    if modality == "func":
        return(t1ws, epis)
    bval = []
    bvec = []
    bvec_t = []
    bval_t = []
    # Look for bval, bvec files for each DWI file
    for scan in epis:
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
    return (t1ws, epis, bval, bvec)


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
