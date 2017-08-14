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
# Created by Eric Bridgeford on 2017-08-09.
# Email: ebridge2@jhu.edu

from bids.grabbids import BIDSLayout
import re
from itertools import product


def sweep_directory(bdir, subj=None, sesh=None, task=None, run=None, modality='dwi'):
    """
    Given a BIDs formatted directory, crawls the BIDs dir and prepares the
    necessary inputs for the NDMG pipeline. Uses regexes to check matches for
    BIDs compliance.
    """
    if modality is 'dwi':
        dwis = []
        bvals = []
        bvecs = []
    elif modality is 'func':
        funcs = []
    anats = []
    layout = BIDSLayout(bdir)  # initialize BIDs tree on bdir
    # get all files matching the specific modality we are using
    if subj is None:
        subjs = layout.get_subjects()  # list of all the subjects
    else:
        subjs = as_list(subj)  # make it a list so we can iterate
    for sub in subjs:
        if not sesh:
            seshs = layout.get_sessions(subject=sub)
            seshs += [None]  # in case there are non-session level inputs
        else:
            seshs = as_list(sesh)  # make a list so we can iterate

        if not task:
            tasks = layout.get_tasks(subject=sub)
            tasks += [None]
        else:
            tasks = as_list(task)

        if not run:
            runs = layout.get_runs(subject=sub)
            runs += [None]
        else:
            runs = as_list(run)

        # all the combinations of sessions and tasks that are possible
        for (ses, tas, ru) in product(seshs, tasks, runs):
            # the attributes for our modality img
            mod_attributes = [sub, ses, tas, ru]
            # the keys for our modality img
            mod_keys = ['subject', 'session', 'task', 'run']
            # our query we will use for each modality img
            mod_query = {'modality': modality}
            if modality is 'dwi':
                type_img = 'dwi'  # use the dwi image
            elif modality is 'func':
                type_img = 'bold'  # use the bold image
            mod_query['type'] = type_img

            for attr, key in zip(mod_attributes, mod_keys):
                if attr:
                    mod_query[key] = attr

            anat_attributes = [sub, ses]  # the attributes for our anat img
            anat_keys = ['subject', 'session']  # the keys for our modality img
            # our query for the anatomical image
            anat_query = {'modality': 'anat', 'type': 'T1w',
                          'extensions': 'nii.gz|nii'}
            for attr, key in zip(anat_attributes, anat_keys):
                if attr:
                    anat_query[key] = attr
            # make a query to fine the desired files from the BIDSLayout
            anat = layout.get(**anat_query)
            if modality is 'dwi':
                dwi = layout.get(**merge_dicts(mod_query,
                                               {'extensions': 'nii.gz|nii'}))
                bval = layout.get(**merge_dicts(mod_query,
                                                {'extensions': 'bval'}))
                bvec = layout.get(**merge_dicts(mod_query,
                                                {'extensions': 'bvec'}))
                if (anat and dwi and bval and bvec):
                    for (dw, bva, bve) in zip(dwi, bval, bvec):
                        if dw.filename not in dwis:

                            # if all the required files exist, append by the first
                            # match (0 index)
                            anats.append(anat[0].filename)
                            dwis.append(dw.filename)
                            bvals.append(bva.filename)
                            bvecs.append(bve.filename)
            elif modality is 'func':
                func = layout.get(**merge_dicts(mod_query,
                                                {'extensions': 'nii.gz|nii'}))
                if func and anat:
                    for fun in func:
                        if fun.filename not in funcs:
                            funcs.append(fun.filename)
                            anats.append(anat[0].filename)
    if modality is 'dwi':
        return (dwis, bvals, bvecs, anats)
    elif modality is 'func':
        return (funcs, anats)


def as_list(x):
    """
    A function to convert an item to a list if it is not, or pass
    it through otherwise.
    """
    if not isinstance(x, list):
        return list(x)
    else:
        return x


def merge_dicts(x, y):
    """
    A function to merge two dictionaries, making it easier for us to make
    modality specific queries for dwi images (since they have variable
    extensions due to having an nii.gz, bval, and bvec file).
    """
    z = x.copy()
    z.update(y)
    return z


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
