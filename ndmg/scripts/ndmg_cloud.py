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

import warnings

warnings.simplefilter("ignore")
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
import ast
import subprocess

participant_templ = 'https://github.com/neurodata/ndmg/blob/dev-dmri-fmri/templates/ndmg_cloud_participant.json'

def batch_submit(bucket, path, jobdir, credentials=None, state='participant',
                 debug=False, dataset=None, log=False, stc=None, mode='dwi',
                 bg=False):
    """
    Searches through an S3 bucket, gets all subject-ids, creates json files
    for each, submits batch jobs, and returns list of job ids to query status
    upon later.
    """
    group = state == 'group'
    print(("Getting list from s3://{}/{}/...".format(bucket, path)))
    threads = crawl_bucket(bucket, path, group, mode=mode)

    print("Generating job for each subject...")
    jobs = create_json(bucket, path, threads, jobdir, group, credentials,
                       debug, dataset, log, stc, mode, bg)

    print("Submitting jobs to the queue...")
    ids = submit_jobs(jobs, jobdir)


def crawl_bucket(bucket, path, group=False, mode='dwi'):
    """
    Gets subject list for a given S3 bucket and path
    """
    if group:
        if mode == 'dwi':
            cmd = 'aws s3 ls s3://{}/{}/graphs/'.format(bucket, path)
        else:
            cmd = 'aws s3 ls s3://{}/{}/connectomes/'.format(bucket, path)
        out = subprocess.check_output(cmd, shell=True)
        atlases = re.findall('PRE (.+)/', out)
        print(("Atlas IDs: " + ", ".join(atlases)))
        return atlases
    else:
        cmd = 'aws s3 ls s3://{}/{}/'.format(bucket, path)
        out = subprocess.check_output(cmd, shell=True)
        subjs = re.findall('PRE sub-(.+)/', out.decode('utf-8'))
        cmd = 'aws s3 ls s3://{}/{}/sub-{}/'
        seshs = OrderedDict()
        for subj in subjs:
            out = subprocess.check_output(cmd.format(bucket, path, subj), shell=True)
            sesh = re.findall('ses-(.+)/', out.decode('utf-8'))
            seshs[subj] = sesh if sesh != [] else [None]
        print(("Session IDs: " + ", ".join([subj + '-' + sesh if sesh is not None
                                           else subj
                                           for subj in subjs
                                           for sesh in seshs[subj]])))
        return seshs


def create_json(bucket, path, threads, jobdir, group=False, credentials=None,
                debug=False, dataset=None, log=False, stc=None, mode='dwi',
                bg=False):
    """
    Takes parameters to make jsons
    """
    out = subprocess.check_output("mkdir -p {}".format(jobdir), shell=True)
    out = subprocess.check_output("mkdir -p {}/jobs/".format(jobdir), shell=True)
    out = subprocess.check_output("mkdir -p {}/ids/".format(jobdir), shell=True)
    if group:
        template = group_templ
        atlases = threads
    else:
        template = participant_templ
        seshs = threads
    if not os.path.isfile('{}/{}'.format(jobdir, template.split('/')[-1])):
        cmd = 'wget --quiet -P {} {}'.format(jobdir, template)
        subprocess.check_output(cmd, shell=True)

    with open('{}/{}'.format(jobdir, template.split('/')[-1]), 'r') as inf:
        template = json.load(inf)

    cmd = ['ndmg_bids '] + template['containerOverrides']['command']
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

    # edit mode, bucket, path
    jobs = list()
    cmd[cmd.index('<MODE>')] = mode
    cmd[cmd.index('<BUCKET>')] = bucket
    cmd[cmd.index('<PATH>')] = path
    if bg:
        cmd.append('--big')

    # edit participant-specific values ()
    # loop over every session of every participant
    for subj in seshs.keys():
        print("... Generating job for sub-{}".format(subj))
        # and for each subject number in each participant number,
        for sesh in seshs[subj]:
            # add format-specific commands,
            job_cmd = deepcopy(cmd)
            job_cmd[job_cmd.index('<SUBJ>')] = subj
            if sesh is not None:
                job_cmd += [u'--session_label']
                job_cmd += [u'{}'.format(sesh)]
            if debug:
                job_cmd += [u'--debug']

            # then, grab the template,
            # add additional parameters,
            # make the json file for this iteration,
            # and add the path to its json file to `jobs`.
            job_json = deepcopy(template)
            ver = ndmg.version.replace('.', '-')
            if dataset:
                name = 'ndmg_{}_{}_sub-{}'.format(ver, dataset, subj)
            else:
                name = 'ndmg_{}_sub-{}'.format(ver, subj)
            if sesh is not None:
                name = '{}_ses-{}'.format(name, sesh)
            print(job_cmd)
            job_json['jobName'] = name
            job_json['containerOverrides']['command'] = job_cmd
            job = os.path.join(jobdir, 'jobs', name+'.json')
            with open(job, 'w') as outfile:
                json.dump(job_json, outfile)
            jobs += [job]

    # return list of job jsons
    return jobs


def submit_jobs(jobs, jobdir):
    """
    Give list of jobs to submit, submits them to AWS Batch
    """
    cmd_template = 'aws batch submit-job --cli-input-json file://{}'

    for job in jobs:
        cmd = cmd_template.format(job)
        print(("... Submitting job {}...".format(job)))
        out = subprocess.check_output(cmd, shell=True)
        submission = ast.literal_eval(out.decode('utf-8'))
        print(("Job Name: {}, Job ID: {}".format(submission['jobName'],
                                                submission['jobId'])))
        sub_file = os.path.join(jobdir, 'ids', submission['jobName'] + '.json')
        with open(sub_file, 'w') as outfile:
            json.dump(submission, outfile)
    return 0


def get_status(jobdir, jobid=None):
    """
    Given list of jobs, returns status of each.
    """
    cmd_template = 'aws batch describe-jobs --jobs {}'

    if jobid is None:
        print(("Describing jobs in {}/ids/...".format(jobdir)))
        jobs = os.listdir(jobdir + '/ids/')
        for job in jobs:
            with open('{}/ids/{}'.format(jobdir, job), 'r') as inf:
                submission = json.load(inf)
            cmd = cmd_template.format(submission['jobId'])
            print(("... Checking job {}...".format(submission['jobName'])))
            out = subprocess.check_output(cmd, shell=True)
            status = re.findall('"status": "([A-Za-z]+)",', out.decode('utf-8'))[0]
            print(("... ... Status: {}".format(status)))
        return 0
    else:
        print(("Describing job id {}...".format(jobid)))
        cmd = cmd_template.format(jobid)
        out = subprocess.check_output(cmd, shell=True)
        status = re.findall('"status": "([A-Za-z]+)",', out.decode('utf-8'))[0]
        print(("... Status: {}".format(status)))
        return status


def kill_jobs(jobdir, reason='"Killing job"'):
    """
    Given a list of jobs, kills them all.
    """
    cmd_template1 = 'aws batch cancel-job --job-id {} --reason {}'
    cmd_template2 = 'aws batch terminate-job --job-id {} --reason {}'

    print(("Canelling/Terminating jobs in {}/ids/...".format(jobdir)))
    jobs = os.listdir(jobdir + '/ids/')
    for job in jobs:
        with open('{}/ids/{}'.format(jobdir, job), 'r') as inf:
            submission = json.load(inf)
        jid = submission['jobId']
        name = submission['jobName']
        status = get_status(jobdir, jid)
        if status in ['SUCCEEDED', 'FAILED']:
            print(("... No action needed for {}...".format(name)))
        elif status in ['SUBMITTED', 'PENDING', 'RUNNABLE']:
            cmd = cmd_template1.format(jid, reason)
            print(("... Cancelling job {}...".format(name)))
            out = subprocess.check_output(cmd, shell=True)
        elif status in ['STARTING', 'RUNNING']:
            cmd = cmd_template2.format(jid, reason)
            print(("... Terminating job {}...".format(name)))
            out = subprocess.check_output(cmd, shell=True)
        else:
            print("... Unknown status??")


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

    out = subprocess.check_output('mkdir -p {}'.format(local), shell=True)
    out = subprocess.check_output(cmd, shell=True)



def s3_push_data(bucket, remote, outDir, modifier, creds=True):
    cmd = 'aws s3 cp --exclude "tmp/*" {} s3://{}/{}/{} --recursive --acl public-read'
    cmd = cmd.format(outDir, bucket, remote, modifier)
    if not creds:
        print("Note: no credentials provided, may fail to push big files.")
        cmd += ' --no-sign-request'
    subprocess.check_output(cmd, shell=True)



def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")

    parser.add_argument('state', choices=['participant',
                                          'group',
                                          'status',
                                          'kill'], default='paricipant',
                        help='determines the function to be performed by '
                             'this function.')
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
    parser.add_argument('--log', action='store_true', help='flag to indicate'
                                                           ' log plotting in group analysis.', default=False)
    parser.add_argument('--debug', action='store_true', help='flag to store '
                                                             'temp files along the path of processing.',
                        default=False)
    parser.add_argument('--dataset', action='store', help='Dataset name')
    parser.add_argument('--stc', action='store', choices=['None', 'interleaved',
                                                          'up', 'down'], default='None', help="The slice timing "
                                                                                              "direction to correct. Not necessary.")
    parser.add_argument('--modality', action='store', choices=['func', 'dwi'],
                        help='Pipeline to run', default='dwi')
    parser.add_argument("-b", "--big", action="store", default='False',
                        help="whether or not to produce voxelwise big graph")
    result = parser.parse_args()

    bucket = result.bucket
    path = result.bidsdir
    path = path.strip('/') if path is not None else path
    debug = result.debug
    state = result.state
    creds = result.credentials
    jobdir = result.jobdir
    dset = result.dataset
    log = result.log
    stc = result.stc
    mode = result.modality
    bg = (result.big != 'False')

    if jobdir is None:
        jobdir = './'

    if (bucket is None or path is None) and \
            (state != 'status' and state != 'kill'):
        sys.exit('Requires either path to bucket and data, or the status flag'
                 ' and job IDs to query.\n  Try:\n    ndmg_cloud --help')

    if state == 'status':
        print("Checking job status...")
        get_status(jobdir)
    elif state == 'kill':
        print("Killing jobs...")
        kill_jobs(jobdir)
    elif state == 'group' or state == 'participant':
        print("Beginning batch submission process...")
        batch_submit(bucket, path, jobdir, creds, state, debug, dset, log,
                     stc, mode, bg)

    sys.exit(0)


if __name__ == "__main__":
    main()
