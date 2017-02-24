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

# ndmg_cloud.py
# Created by Greg Kiar on 2017-02-02.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
from collections import OrderedDict
from copy import deepcopy
import ndmg.utils as mgu
import ndmg
import sys
import os
import re
import csv
import boto3
import json

job_template = 'https://raw.githubusercontent.com/neurodata/sic/master/code/ec2/batch/json_files/job_template.json'


def batch_submit(bucket, path, jobdir, credentials=None, debug=False,
                 dataset=None):
    """
    Searches through an S3 bucket, gets all subject-ids, creates json files
    for each, submits batch jobs, and returns list of job ids to query status
    upon later.
    """
    print("Getting subject list from s3://{}/{}/...".format(bucket, path))
    seshs = crawl_bucket(bucket, path)
    print("Generating job for each subject...")
    jobs = create_json(bucket, path, sesh, jobdir, credentials, debug,
                       dataset)
    print("Submitting jobs to the queue...")
    ids = submit_jobs(jobs)


def crawl_bucket(bucket, path):
    """
    Gets subject list for a given S3 bucket and path
    """
    cmd = 'aws s3 ls s3://{}/{}/'.format(bucket, path)
    out, err = mgu().execute_cmd(cmd)
    subjs = re.findall('sub-(.+)/', out)
    cmd = 'aws s3 ls s3://{}/{}/sub-{}/'
    seshs = OrderedDict()
    for subj in subjs:
        out, err = mgu().execute_cmd(cmd.format(bucket, path, subj))
        sesh = re.findall('ses-(.+)/', out)
        seshs[subj] = sesh if sesh != [] else [None]
    print("Session IDs: " + ", ".join([subj+'-'+sesh if sesh is not None
                                       else subj
                                       for subj in subjs
                                       for sesh in seshs[subj]]))
    return seshs


def create_json(bucket, path, seshs, jobdir, credentials=None, debug=False,
                dataset=None):
    """
    Takes parameters to make jsons
    """
    mgu().execute_cmd("mkdir -p {}".format(jobdir))
    mgu().execute_cmd("mkdir -p {}/jobs/".format(jobdir))
    if not os.path.isfile('{}/job_template.json'.format(jobdir)):
        cmd = 'wget --quiet -P {} {}'.format(jobdir, job_template)
        mgu().execute_cmd(cmd)

    with open('{}/job_template.json'.format(jobdir), 'r') as infile:
        template = json.load(infile)
    cmd = template['containerOverrides']['command']
    env = template['containerOverrides']['environment']

    if credentials is not None:
        cred = [line for line in csv.reader(open(credentials))]
        env[0]['value'] = [cred[1][idx]
                           for idx, val in enumerate(cred[0])
                           if "ID" in val][0]  # Adds public key ID to env
        env[1]['value'] = [cred[1][idx]
                           for idx, val in enumerate(cred[0])
                           if "Secret" in val][0]  # Adds secret key to env
    else:
        env = []
    template['containerOverrides']['environment'] = env

    jobs = list()
    cmd[4] = re.sub('(<BUCKET>)', bucket, cmd[4])
    cmd[6] = re.sub('(<PATH>)', path, cmd[6])

    for subj in seshs.keys():
        print("... Generating job for sub-{}".format(subj))
        for sesh in seshs[subj]:
            job_cmd = deepcopy(cmd)
            job_cmd[8] = re.sub('(<SUBJ>)', subj, job_cmd[8])
            if sesh is not None:
                job_cmd += [u'--session_label']
                job_cmd += [u'{}'.format(sesh)]
            if debug:
                job_cmd += [u'--debug']

            job_json = deepcopy(template)
            ver = ndmg.version.replace('.', '-')
            if dataset:
                name = 'ndmg-{}_{}_sub-{}'.format(ver, dataset, subj)
            else:
                name = 'ndmg_{}_sub-{}'.format(ver, subj)
            if sesh is not None:
                name = '{}_ses-{}'.format(name, sesh)
            job_json['jobName'] = name
            job_json['containerOverrides']['command'] = job_cmd
            job = os.path.join(jobdir, 'jobs', name+'.json')
            with open(job, 'w') as outfile:
                json.dump(job_json, outfile)
            jobs += [job]
    return jobs


def submit_jobs(jobs):
    """
    Give list of jobs to submit, submits them to AWS Batch
    """
    cmd_template = 'aws batch submit-job --cli-input-json file://{}'

    for job in jobs:
        cmd = cmd_template.format(job)
        print("... Submitting job {}...".format(job))
        out, err = mgu().execute_cmd(cmd)
        print("Out: {}".format(out))
        print("Err: {}".format(err))
    return 0


def get_status(jobdir):
    """
    Given list of jobs, returns status of each.
    """
    # for job in os.path.listdir(jobdir):
    #    pass
    # TODO: this
    # return 0
    print("This has yet to be implemented - come back soon!")


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")

    parser.add_argument('--bucket', help='The S3 bucket with the input dataset'
                        ' formatted according to the BIDS standard.')
    parser.add_argument('--bidsdir', help='The directory where the dataset'
                        ' lives on the S3 bucket should be stored. If you'
                        ' level analysis this folder should be prepopulated'
                        ' with the results of the participant level analysis.')
    parser.add_argument('--jobdir', action='store', help='Dir of batch jobs to'
                        ' generate/check up on.')
    parser.add_argument('--credentials', action='store', help='AWS formatted'
                        ' csv of credentials.')
    parser.add_argument('--debug', action='store_true', help='flag to store '
                        'temp files along the path of processing.',
                        default=False)
    parser.add_argument('--status', action='store_true', help='flag to check'
                        'status of jobs rather than launch them.',
                        default=False)
    parser.add_argument('--dataset', action='store', help='Dataset name')
    result = parser.parse_args()

    bucket = result.bucket
    remo = result.bidsdir
    debug = result.debug
    status = result.status
    creds = result.credentials
    jobdir = result.jobdir
    dset = result.dataset
    if jobdir is None:
        jobdir = './'

    if (bucket is None or remo is None) and (status is False):
        sys.exit('Requires either path to bucket and data, or the status flag'
                 ' and job IDs to query.\n  Try:\n    ndmg_cloud --help')

    if status:
        print("Checking job status...")
        get_status(jobdir)
    else:
        print("Beginning batch submission process...")
        batch_submit(bucket, remo, jobdir, creds, debug, dset)

    sys.exit(0)


if __name__ == "__main__":
    main()
