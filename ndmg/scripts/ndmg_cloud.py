#!/usr/bin/env python

"""
ndmg.scripts.ndmg_cloud
~~~~~~~~~~~~~~~~~~~~~~~

Contains functionality for running ndmg in batch on AWS.
For a tutorial on setting this up, see here : https://github.com/neurodata/ndmg/blob/deploy/tutorials/Batch.ipynb
"""

# standard library imports
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
from pathlib import Path

# package imports
import boto3

# ndmg imports
import ndmg
from ndmg.utils.cloud_utils import get_credentials
from ndmg.utils.cloud_utils import get_matching_s3_objects
from ndmg.utils.cloud_utils import s3_client

# TODO : grab this locally, using pkg_resources
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
    """Searches through an S3 bucket, gets all subject-ids, creates json files for each,
    submits batch jobs, and returns list of job ids to query status upon later

    Parameters
    ----------
    bucket : str
        The S3 bucket with the input dataset formatted according to the BIDS standard.
    path : str
        The directory where the dataset is stored on the S3 bucket
    jobdir : str
        Directory of batch jobs to generate/check up on
    credentials : [type], optional
        AWS formatted csv of credentials, by default None
    state : str, optional
        determines the function to be performed by this function ("participant", "status", "kill"), by default "participant"
    debug : bool, optional
        flag whether to save temp files along the path of processing, by default False
    dataset : str, optional
        Name given to the output directory containing analyzed data set "ndmg-<version>-<dataset>", by default None
    log : bool, optional
        flag to indicate log ploting in group analysis, by default False
    bg : bool, optional
        whether or not to produce voxelwise big graph, by default False
    modif : str, optional
        Name of folder on s3 to push to. If empty, push to a folder with ndmg's version number, by default ""
    reg_style : str, optional
        Space for tractography, by default ""
    mod_type : str, optional
        Determinstic (det) or probabilistic (prob) tracking, by default ""
    """

    print(f'Getting list from s3://{bucket}/{path}/...')
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
    """Gets subject list for a given s3 bucket and path

    Parameters
    ----------
    bucket : str
        s3 bucket
    path : str
        The directory where the dataset is stored on the S3 bucket
    jobdir : str
        Directory of batch jobs to generate/check up on

    Returns
    -------
    OrderedDict
        dictionary containing all subjects and sessions from the path location
    """

    # if jobdir has seshs info file in it, use that instead
    sesh_path = f'{jobdir}/seshs.json'
    if os.path.isfile(sesh_path):
        print("seshs.json found -- loading bucket info from there")
        with open(sesh_path, "r") as f:
            seshs = json.load(f)
        print("Information obtained from s3.")
        return seshs

    # set up bucket crawl
    subj_pattern = r"(?<=sub-)(\w*)(?=/ses)"
    sesh_pattern = r"(?<=ses-)(\d*)"
    all_subfiles = get_matching_s3_objects(bucket, path + "/sub-")
    subjs = list(set(re.findall(subj_pattern, obj)[0] for obj in all_subfiles))
    seshs = OrderedDict()

    # populate seshs
    for subj in subjs:
        prefix = f'{path}/sub-{subj}/'
        all_seshfiles = get_matching_s3_objects(bucket, prefix)
        sesh = list(set([re.findall(sesh_pattern, obj)[0] for obj in all_seshfiles]))
        if sesh != []:
            seshs[subj] = sesh
            print(f'{subj} added to seshs.')
        else:
            seshs[subj] = None
            print(f'{subj} not added (no sessions).')


    # print session IDs and create json cache
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
    print(f'{sesh_path} created.')
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
    """Creates the json files for each of the jobs

    Parameters
    ----------
    bucket : str
        The S3 bucket with the input dataset formatted according to the BIDS standard.
    path : str
        The directory where the dataset is stored on the S3 bucket
    threads : OrderedDict
        dictionary containing all subjects and sessions from the path location
    jobdir : str
        Directory of batch jobs to generate/check up on
    credentials : [type], optional
        AWS formatted csv of credentials, by default None
    debug : bool, optional
        flag whether to save temp files along the path of processing, by default False
    dataset : [type], optional
        Name given to the output directory containing analyzed data set "ndmg-<version>-<dataset>", by default None
    bg : bool, optional
        whether or not to produce voxelwise big graph, by default False
    modif : str, optional
        Name of folder on s3 to push to. If empty, push to a folder with ndmg's version number, by default ""
    reg_style : str, optional
        Space for tractography, by default ""
    mod_type : str, optional
        Determinstic (det) or probabilistic (prob) tracking, by default ""

    Returns
    -------
    list
        list of job jsons
    """
    jobsjson = f'{jobdir}/jobs.json'
    if os.path.isfile(jobsjson):
        with open(jobsjson, "r") as f:
            jobs = json.load(f)
        return jobs

    # set up infrastructure
    out = subprocess.check_output(f'mkdir -p {jobdir}', shell=True)
    out = subprocess.check_output(f'mkdir -p {jobdir}/jobs/', shell=True)
    out = subprocess.check_output(f'mkdir -p {jobdir}/ids/', shell=True)
    template = participant_templ
    seshs = threads

    # make template
    if not os.path.isfile(f'{jobdir}/{template.split("/")[-1]}'):
        cmd = f'wget --quiet -P {jobdir} {template}'
        subprocess.check_output(cmd, shell=True)

    with open(f'{jobdir}/{template.split("/")[-1]}', "r") as inf:
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
        cmd.insert(cmd.index("--push_data") + 1, u"--modif")
        cmd.insert(cmd.index("--push_data") + 2, modif)

    # edit participant-specific values ()
    # loop over every session of every participant
    for subj in seshs.keys():
        print(f'... Generating job for sub-{subj}')
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
            ver = ndmg.__version__.replace(".", "-")
            if dataset:
                name = f'ndmg_{ver}_{dataset}_sub-{subj}'
            else:
                name = f'ndmg_{ver}_sub-{subj}'
            if sesh is not None:
                name = f'{name}_ses-{sesh}'
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
    """Give list of jobs to submit, submits them to AWS Batch

    Parameters
    ----------
    jobs : list
        Name of the json files for all jobs to submit
    jobdir : str
        Directory of batch jobs to generate/check up on

    Returns
    -------
    int
        0
    """

    batch = s3_client(service="batch")
    cmd_template = "--cli-input-json file://{}"

    for job in jobs:
        with open(job, "r") as f:
            kwargs = json.load(f)
        print(f'... Submitting job {job}...')
        submission = batch.submit_job(**kwargs)
        print(
            (
                f'Job Name: {submission["jobName"]}, Job ID: {submission["jobId"]}'
            )
        )
        sub_file = os.path.join(jobdir, "ids", submission["jobName"] + ".json")
        with open(sub_file, "w") as outfile:
            json.dump(submission, outfile)
        print("Submitted.")
    return 0


def kill_jobs(jobdir, reason='"Killing job"'):
    """Given a list of jobs, kills them all

    Parameters
    ----------
    jobdir : str
        Directory of batch jobs to generate/check up on
    reason : str, optional
        Task you want to perform on the jobs, by default '"Killing job"'
    """

    cmd_template1 = "aws batch cancel-job --job-id {} --reason {}"
    cmd_template2 = "aws batch terminate-job --job-id {} --reason {}"

    print(f'Cancelling/Terminating jobs in {jobdir}/ids/...')
    jobs = os.listdir(jobdir + "/ids/")
    batch = s3_client(service="batch")
    jids = []
    names = []

    # grab info about all the jobs
    for job in jobs:
        with open(f'{jobdir}/ids/{job}', "r") as inf:
            submission = json.load(inf)
        jid = submission["jobId"]
        name = submission["jobName"]
        jids.append(jid)
        names.append(name)

    for jid in jids:
        print(f'Terminating job {jid}')
        batch.terminate_job(jobId=jid, reason=reason)


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
            Path(jobdir).mkdir(parents=True)
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