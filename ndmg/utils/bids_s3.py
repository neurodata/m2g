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

# bids_s3.py
# Created by Greg Kiar on 2016-07-29.
# Email: gkiar@jhu.edu

import ndmg.utils as mgu
import sys
import boto3


def get_data(bucket, remote_path, local, subj=None, public=True):
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
    cmd = 'aws'
    if public:
        cmd += ' --no-sign-request --region=us-east-1'
    cmd = "".join([cmd, ' s3 cp --recursive s3://', bucket, '/',
                   remote_path])
    if subj is not None:
        cmd = "".join([cmd, '/sub-', subj])
        std, err = mgu().execute_cmd('mkdir -p ' + local + '/sub-' + subj)
        local += '/sub-' + subj

    cmd = "".join([cmd, ' ', local])
    std, err = mgu().execute_cmd(cmd)
    return
