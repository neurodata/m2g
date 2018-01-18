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

import ndmg.utils as mgu
import os.path as op
import os
import sys
import boto3
from glob import glob

def crawl_bids_directory(inDir, subjs, sesh):
    """
    Given a BIDS directory and optionally list of sessions and subjects,
    crawls the path and returns pointers to all relevant files for analysis.
    """
    if subjs is None:
        subj_dirs = glob(op.join(inDir, "sub-*"))
        subjs = [subj_dir.split("-")[-1] for subj_dir in subj_dirs]

    bvec = []
    bval = []
    dwi = []
    anat = []
    func = []

    for subj in subjs:
        if sesh is not None:
            anat_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                  "anat", "*_T1w.nii*"))
            dwi_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                 "dwi", "*_dwi.nii*"))
            func_t = glob(op.join(inDir, "sub-{}/ses-{}".format(subj, sesh),
                                 "func", "*_bold.nii*"))
        else:
            anat_t = glob(op.join(inDir, "sub-{}".format(subj), "anat",
                                  "*_T1w.nii*")) +\
                     glob(op.join(inDir, "sub-{}".format(subj), "ses-*",
                                  "anat", "*_T1w.nii*"))
            dwi_t = glob(op.join(inDir, "sub-{}".format(subj), "dwi",
                                 "*_dwi.nii*")) +\
                    glob(op.join(inDir, "sub-{}".format(subj), "ses-*",
                                 "dwi", "*_dwi.nii*"))
            func_t = glob(op.join(inDir, "sub-{}".format(subj), "func",
                                  "*_bold.nii*")) +\
                     glob(op.join(inDir, "sub-{}".format(subj), "ses-*",
                                  "func", "*_bold.nii*"))
        dwi = dwi + dwi_t
        anat = anat + anat_t
        func = func + func_t

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
    return (anat, func, dwi, bvec, bval)


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
