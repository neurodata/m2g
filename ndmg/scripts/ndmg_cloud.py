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
# Edited a ton by Alex Loftus
# Email: gkiar@jhu.edu, aloftus2@jhu.edu

#%%
import subprocess
import ast
import csv
import re
import os
import sys
import json
from copy import deepcopy
from collections import OrderedDict
from argparse import ArgumentParser
import warnings
import shutil
import time

import boto3

import ndmg
import ndmg.utils as mgu
from ndmg.utils.s3_utils import get_credentials, get_matching_s3_objects, s3_client

participant_templ = "https://raw.githubusercontent.com/neurodata/ndmg/staging/templates/ndmg_cloud_participant.json"


def batch_submit(
    bucket,
    path,
    jobdir,
    credentials=None,
    state="participant",
    debug=False,
    dataset=None,
    log=False,
    bg=False,
    modif="",
    reg_style="",
    mod_type="",
):
    """
    Searches through an S3 bucket, gets all subject-ids, creates json files
    for each, submits batch jobs, and returns list of job ids to query status
    upon later.
    """
    print(("Getting list from s3://{}/{}/...".format(bucket, path)))
    threads = crawl_bucket(bucket, path, jobdir)

    print("Generating job for each subject...")
    jobs = create_json(
        bucket,
        path,
        threads,
        jobdir,
        credentials,
        debug,
        dataset,
        bg,
        modif=modif,
        reg_style=reg_style,
    )

    print("Submitting jobs to the queue...")
    ids = submit_jobs(jobs, jobdir)


def crawl_bucket(bucket, path, jobdir):
    """
    Gets subject list for a given S3 bucket and path
    """
    # if jobdir has seshs info file in it, use that instead
    sesh_path = "{}/seshs.json".format(jobdir)
    if os.path.isfile(sesh_path):
        print("seshs.json found -- loading bucket info from there")
        with open(sesh_path, "r") as f:
            seshs = json.load(f)
        print("Information obtained from s3.")
        return seshs

    subj_pattern = r"(?<=sub-)(\w*)(?=/ses)"
    sesh_pattern = r"(?<=ses-)(\d*)"
    all_subfiles = get_matching_s3_objects(bucket, path + "/sub-")
    subjs = list(set(re.findall(subj_pattern, obj)[0] for obj in all_subfiles))
    # cmd = "aws s3 ls s3://{}/{}/".format(bucket, path)
    # try:
    #     ACCESS, SECRET = get_credentials()
    #     os.environ["AWS_ACCESS_KEY_ID"] = ACCESS
    #     os.environ["AWS_SECRET_ACCESS_KEY"] = SECRET
    # except:
    #     cmd += " --no-sign-request"
    # out = subprocess.check_output(cmd, shell=True)
    # pattern = r"(?<=sub-)(\w*)(?=/ses)"
    # subjs = re.findall(pattern, out.decode("utf-8"))
    # cmd = "aws s3 ls s3://{}/{}/sub-{}/"
    # if not ACCESS:
    #     cmd += " --no-sign-request"
    seshs = OrderedDict()
    # TODO : use boto3 for this.
    for subj in subjs:
        prefix = path + "/sub-{}/".format(subj)
        all_seshfiles = get_matching_s3_objects(bucket, prefix)
        sesh = list(set([re.findall(sesh_pattern, obj)[0] for obj in all_seshfiles]))

        # cmd = cmd.format(bucket, path, subj)
        # out = subprocess.check_output(cmd, shell=True)  # TODO: get this information outside of a loop
        # sesh = re.findall("ses-(.+)/", out.decode("utf-8"))
        if sesh != []:
            seshs[subj] = sesh
            print("{} added to seshs.".format(subj))
        else:
            seshs[subj] = None
            print("{} not added (no sessions).".format(subj))
        # seshs[subj] = sesh if sesh != [] else [None]
    print(
        (
            "Session IDs: "
            + ", ".join(
                [
                    subj + "-" + sesh if sesh is not None else subj
                    for subj in subjs
                    for sesh in seshs[subj]
                ]
            )
        )
    )
    with open(sesh_path, "w") as f:
        json.dump(seshs, f)
    print("{} created.".format(sesh_path))
    print("Information obtained from s3.")
    return seshs


def create_json(
    bucket,
    path,
    threads,
    jobdir,
    credentials=None,
    debug=False,
    dataset=None,
    bg=False,
    modif="",
    reg_style="",
    mod_type="",
):
    """
    Takes parameters to make jsons
    """
    jobsjson = "{}/jobs.json".format(jobdir)
    if os.path.isfile(jobsjson):
        with open(jobsjson, "r") as f:
            jobs = json.load(f)
        return jobs

    # set up infrastructure
    out = subprocess.check_output("mkdir -p {}".format(jobdir), shell=True)
    out = subprocess.check_output("mkdir -p {}/jobs/".format(jobdir), shell=True)
    out = subprocess.check_output("mkdir -p {}/ids/".format(jobdir), shell=True)
    template = participant_templ
    seshs = threads

    # make template
    if not os.path.isfile("{}/{}".format(jobdir, template.split("/")[-1])):
        cmd = "wget --quiet -P {} {}".format(jobdir, template)
        subprocess.check_output(cmd, shell=True)

    with open("{}/{}".format(jobdir, template.split("/")[-1]), "r") as inf:
        template = json.load(inf)

    cmd = template["containerOverrides"]["command"]
    env = template["containerOverrides"]["environment"]

    # TODO : This checks for any credentials csv file, rather than `/.aws/credentials`.
    # modify template
    if credentials is not None:
        env[0]["value"], env[1]["value"] = get_credentials()
    else:
        env = []
    template["containerOverrides"]["environment"] = env

    # edit non-defaults
    jobs = []
    cmd[cmd.index("<BUCKET>")] = bucket
    cmd[cmd.index("<PATH>")] = path

    # edit defaults if necessary
    if reg_style:
        cmd[cmd.index("--sp") + 1] = reg_style
    if mod_type:
        cmd[cmd.index("--mod") + 1] = reg_style
    if bg:
        cmd.append("--big")
    if modif:
        cmd.insert(19, u"--modif")
        cmd.insert(20, modif)

    # edit participant-specific values ()
    # loop over every session of every participant
    for subj in seshs.keys():
        print("... Generating job for sub-{}".format(subj))
        # and for each subject number in each participant number,
        for sesh in seshs[subj]:
            # add format-specific commands,
            job_cmd = deepcopy(cmd)
            job_cmd[job_cmd.index("<SUBJ>")] = subj
            if sesh is not None:
                job_cmd.insert(7, u"--session_label")
                job_cmd.insert(8, u"{}".format(sesh))
            if debug:
                job_cmd += [u"--debug"]

            # then, grab the template,
            # add additional parameters,
            # make the json file for this iteration,
            # and add the path to its json file to `jobs`.
            job_json = deepcopy(template)
            ver = ndmg.VERSION.replace(".", "-")
            if dataset:
                name = "ndmg_{}_{}_sub-{}".format(ver, dataset, subj)
            else:
                name = "ndmg_{}_sub-{}".format(ver, subj)
            if sesh is not None:
                name = "{}_ses-{}".format(name, sesh)
            print(job_cmd)
            job_json["jobName"] = name
            job_json["containerOverrides"]["command"] = job_cmd
            job = os.path.join(jobdir, "jobs", name + ".json")
            with open(job, "w") as outfile:
                json.dump(job_json, outfile)
            jobs += [job]

    # return list of job jsons
    with open(jobsjson, "w") as f:
        json.dump(jobs, f)
    return jobs


def submit_jobs(jobs, jobdir):
    """
    Give list of jobs to submit, submits them to AWS Batch
    """
    batch = s3_client(service="batch")
    cmd_template = "--cli-input-json file://{}"
    # cmd_template = batch.submit_jobs

    for job in jobs:
        # use this to start wherever
        # if jobs.index(job) >= jobs.index('/jobs/jobs/ndmg_0-1-2_SWU4_sub-0025768_ses-1.json'):
        with open(job, "r") as f:
            kwargs = json.load(f)
        print(("... Submitting job {}...".format(job)))
        submission = batch.submit_job(**kwargs)
        # out = subprocess.check_output(cmd, shell=True)
        # time.sleep(0.1)  # jobs sometimes hang, seeing if this helps
        # submission = ast.literal_eval(out.decode("utf-8"))
        print(
            (
                "Job Name: {}, Job ID: {}".format(
                    submission["jobName"], submission["jobId"]
                )
            )
        )
        sub_file = os.path.join(jobdir, "ids", submission["jobName"] + ".json")
        with open(sub_file, "w") as outfile:
            json.dump(submission, outfile)
        print("Submitted.")
    return 0


def get_status(jobdir, jobid=None):
    """
    Given list of jobs, returns status of each.
    """
    cmd_template = "aws batch describe-jobs --jobs {}"

    if jobid is None:
        print(("Describing jobs in {}/ids/...".format(jobdir)))
        jobs = os.listdir(jobdir + "/ids/")
        for job in jobs:
            with open("{}/ids/{}".format(jobdir, job), "r") as inf:
                submission = json.load(inf)
            cmd = cmd_template.format(submission["jobId"])
            print(("... Checking job {}...".format(submission["jobName"])))
            out = subprocess.check_output(cmd, shell=True)
            status = re.findall('"status": "([A-Za-z]+)",', out.decode("utf-8"))[0]
            print(("... ... Status: {}".format(status)))
        return 0
    else:
        print(("Describing job id {}...".format(jobid)))
        cmd = cmd_template.format(jobid)
        out = subprocess.check_output(cmd, shell=True)
        status = re.findall('"status": "([A-Za-z]+)",', out.decode("utf-8"))[0]
        print(("... Status: {}".format(status)))
        return status


def kill_jobs(jobdir, reason='"Killing job"'):
    """
    Given a list of jobs, kills them all.
    """
    cmd_template1 = "aws batch cancel-job --job-id {} --reason {}"
    cmd_template2 = "aws batch terminate-job --job-id {} --reason {}"

    print(("Canelling/Terminating jobs in {}/ids/...".format(jobdir)))
    jobs = os.listdir(jobdir + "/ids/")
    batch = s3_client(service="batch")
    jids = []
    names = []

    # grab info about all the jobs
    for job in jobs:
        with open("{}/ids/{}".format(jobdir, job), "r") as inf:
            submission = json.load(inf)
        jid = submission["jobId"]
        name = submission["jobName"]
        jids.append(jid)
        names.append(name)

    for jid in jids:
        print("Terminating job {}".format(jid))
        batch.terminate_job(jobId=jid, reason=reason)
        # status = get_status(jobdir, jid)
        # if status in ["SUCCEEDED", "FAILED"]:
        #     print(("... No action needed for {}...".format(name)))
        # elif status in ["SUBMITTED", "PENDING", "RUNNABLE"]:
        #     cmd = cmd_template1.format(jid, reason)
        #     print(("... Cancelling job {}...".format(name)))
        #     out = subprocess.check_output(cmd, shell=True)
        # elif status in ["STARTING", "RUNNING"]:
        #     cmd = cmd_template2.format(jid, reason)
        #     print(("... Terminating job {}...".format(name)))
        #     out = subprocess.check_output(cmd, shell=True)
        # else:
        #     print("... Unknown status??")


#%%
def main():
    parser = ArgumentParser(
        description="This is a pipeline for running BIDs-formatted diffusion MRI datasets through AWS S3 to produce connectomes."
    )

    parser.add_argument(
        "state",
        choices=["participant", "status", "kill"],
        default="participant",
        help="determines the function to be performed by " "this function.",
    )
    parser.add_argument(
        "--bucket",
        help="The S3 bucket with the input dataset"
        " formatted according to the BIDS standard.",
    )
    parser.add_argument(
        "--bidsdir",
        help="The directory where the dataset"
        " lives on the S3 bucket should be stored. If you"
        " level analysis this folder should be prepopulated"
        " with the results of the participant level analysis.",
    )
    parser.add_argument(
        "--jobdir", action="store", help="Dir of batch jobs to" " generate/check up on."
    )
    parser.add_argument(
        "--credentials", action="store", help="AWS formatted" " csv of credentials."
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="flag to indicate" " log plotting in group analysis.",
        default=False,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="flag to store " "temp files along the path of processing.",
        default=False,
    )
    parser.add_argument("--dataset", action="store", help="Dataset name")
    parser.add_argument(
        "-b",
        "--big",
        action="store",
        default="False",
        help="whether or not to produce voxelwise big graph",
    )
    parser.add_argument(
        "--modif",
        action="store",
        help="Name of folder on s3 to push to. If empty, push to a folder with ndmg's version number.",
        default="",
    )
    parser.add_argument(
        "--sp",
        action="store",
        help="Space for tractography. Default is native.",
        default="native",
    )
    parser.add_argument(
        "--mod",
        action="store",
        help="Determinstic (det) or probabilistic (prob) tracking. Default is det.",
        default="det",
    )

    result = parser.parse_args()

    bucket = result.bucket
    path = result.bidsdir
    path = path.strip("/") if path is not None else path
    debug = result.debug
    state = result.state
    creds = result.credentials
    jobdir = result.jobdir
    dset = result.dataset
    log = result.log
    bg = result.big != "False"
    modif = result.modif
    reg_style = result.sp
    mod_type = result.mod

    if jobdir is None:
        jobdir = "./"

    if (bucket is None or path is None) and (state != "status" and state != "kill"):
        sys.exit(
            "Requires either path to bucket and data, or the status flag"
            " and job IDs to query.\n  Try:\n    ndmg_cloud --help"
        )

    if state == "status":
        print("Checking job status...")
        get_status(jobdir)
    elif state == "kill":
        print("Killing jobs...")
        kill_jobs(jobdir)
    elif state == "participant":
        print("Beginning batch submission process...")
        if not os.path.exists(jobdir):
            print("job directory not found. Creating...")
            os.mkdir(jobdir)
        batch_submit(
            bucket,
            path,
            jobdir,
            creds,
            state,
            debug,
            dset,
            log,
            bg,
            modif=modif,
            reg_style=reg_style,
            mod_type=mod_type,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
