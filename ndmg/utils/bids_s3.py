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

from subprocess import Popen, PIPE
from os.path import expanduser
from ndmg.scripts.ndmg_setup import get_files
from ndmg.scripts.ndmg_pipeline import ndmg_pipeline

import ndmg.utils as mgu
import os.path as op

import os
import sys
import boto3

def get_data(bucket, remote_path, inDir):
    client = boto3.client('s3')
    bkts = [bk['Name'] for bk in client.list_buckets()['Buckets']]
    if bucket not in bkts:
        sys.exit("Error: could not locate bucket. Available buckets: " +\
                 ", ".join(bkts))

    cmd = "".join(['aws s3 cp --recursive s3://', bucket, '/',
                   remote_path, ' ', inDir])
    std, err = mgu().execute_cmd(cmd)
    return
