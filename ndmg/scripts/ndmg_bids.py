#ble to work out !/usr/bin/env python

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

# ndmg_bids.py
# Created by Greg Kiar on 2016-07-25.
# edited by Eric Bridgeford to incorporate fMRI, multi-threading, and
# big-graph generation.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
from subprocess import Popen, PIPE
from os.path import expanduser
from ndmg.scripts.ndmg_setup import get_files
from ndmg.utils.bids_utils import *
from ndmg.scripts.ndmg_dwi_pipeline import ndmg_dwi_pipeline
from ndmg.scripts.ndmg_func_pipeline import ndmg_func_pipeline
from ndmg.utils.bids_utils import *
from ndmg.stats.qa_graphs import *
from ndmg.stats.qa_graphs_plotting import *
from ndmg.stats.group_func import group_func
from glob import glob
import ndmg.utils as mgu
import ndmg
import os.path as op
import os
import sys
from multiprocessing import Pool
from functools import partial
import traceback


atlas_dir = '/ndmg_atlases'  # This location bc it is convenient for containers

# Data structure:
# sub-<subject id>/
#   ses-<session id>/
#     anat/
#       sub-<subject id>_ses-<session id>_T1w.nii.gz
#     dwi/
#       sub-<subject id>_ses-<session id>_dwi.nii.gz
#   *   sub-<subject id>_ses-<session id>_dwi.bval
#   *   sub-<subject id>_ses-<session id>_dwi.bvec
#
# *these files can be anywhere up stream of the dwi data, and are inherited.


def get_atlas(atlas_dir, modality='dwi'):
    """
    Given the desired location for atlases and the type of processing, ensure
    we have all the atlases and parcellations.
    """
    if modality == 'dwi':
        atlas = op.join(atlas_dir, 'atlas/MNI152NLin6_res-1x1x1_T1w.nii.gz')
        atlas_mask = op.join(atlas_dir,
                             'mask/MNI152NLin6_res-1x1x1_T1w_brainmask.nii.gz')
        labels= [harvlab + 'cort-maxprob-thr25_res-1x1x1.nii.gz',
                 harvlab + 'sub-maxprob-thr25_res-1x1x1.nii.gz',
                 'slab1067_res-1x1x1.nii.gz', 'slab907_res-1x1x1.nii.gz',
                 'aal_res-1x1x1.nii.gz', 'brodmann_res-1x1x1.nii.gz',
                 'desikan_res-1x1x1.nii.gz', 'pp264_res-1x1x1.nii.gz',
                 'CPAC200_res-1x1x1.nii.gz', 'DS00071_res-1x1x1.nii.gz',
                 'DS00096_res-1x1x1.nii.gz', 'DS00108_res-1x1x1.nii.gz',
                 'DS00140_res-1x1x1.nii.gz', 'DS00195_res-1x1x1.nii.gz',
                 'DS00278_res-1x1x1.nii.gz', 'DS00350_res-1x1x1.nii.gz',
                 'DS00446_res-1x1x1.nii.gz', 'DS00583_res-1x1x1.nii.gz',
                 'DS00833_res-1x1x1.nii.gz', 'DS01216_res-1x1x1.nii.gz',
                 'DK_res-1x1x1.nii.gz', 'JHU_res-1x1x1.nii.gz',
                 'tissue_res-1x1x1.nii.gz', 'hemispheric_res-1x1x1.nii.gz']
 
        labels = [op.join(atlas_dir, 'label', l) for l in labels]
        fils = labels + [atlas, atlas_mask]
    if modality == 'func':
        atlas = op.join(atlas_dir, 'atlas/MNI152NLin6_res-2x2x2_T1w.nii.gz')
        atlas_brain = op.join(atlas_dir, 'atlas/' +
                              'MNI152NLin6_res-2x2x2_T1w_brain.nii.gz')
        atlas_mask = op.join(atlas_dir,
                             'mask/MNI152NLin6_res-2x2x2_T1w_brainmask.nii.gz')
        lv_mask = op.join(atlas_dir, "mask/HarvardOxford_variant-" +
                          "lateral-ventricles-thr25" +
                          "_res-2x2x2_brainmask.nii.gz")
        harvlab = 'HarvardOxford'
        labels= [harvlab + 'cort-maxprob-thr25_res-2x2x2.nii.gz',
                 harvlab + 'sub-maxprob-thr25_res-2x2x2.nii.gz',
                 'aal_res-2x2x2.nii.gz', 'brodmann_res-2x2x2.nii.gz',
                 'desikan_res-2x2x2.nii.gz', 'pp264_res-2x2x2.nii.gz',
                 'CPAC200_res-2x2x2.nii.gz', 'DS00071_res-2x2x2.nii.gz',
                 'DS00096_res-2x2x2.nii.gz', 'DS00108_res-2x2x2.nii.gz',
                 'DS00140_res-2x2x2.nii.gz', 'DS00195_res-2x2x2.nii.gz',
                 'DS00278_res-2x2x2.nii.gz', 'DS00350_res-2x2x2.nii.gz',
                 'DS00446_res-2x2x2.nii.gz', 'DS00583_res-2x2x2.nii.gz',
                 'DS00833_res-2x2x2.nii.gz', 'DS01216_res-2x2x2.nii.gz',
                 'DK_res-2x2x2.nii.gz', 'JHU_res-2x2x2.nii.gz',
                 'tissue_res-2x2x2.nii.gz', 'hemispheric_res-2x2x2.nii.gz']
 
        labels = [op.join(atlas_dir, 'label', l) for l in labels]
        fils = labels + [atlas, atlas_mask, atlas_brain, lv_mask]

    ope = op.exists
    for f in fils:
        if not ope(f):
            print(f)
    if any(not ope(f) for f in fils):
        print("Cannot find atlas information; downloading...")
        mgu.execute_cmd('mkdir -p ' + atlas_dir)
        cmd = 'aws s3 cp --no-sign-request s3://mrneurodata/data/'
        cmd += 'resources/ndmg_atlases.zip {}'.format(atlas_dir)
        mgu.execute_cmd(cmd)
        cmd = 'unzip {}'.format(op.join(atlas_dir, 'ndmg_atlases.zip'))
        mgu.execute_cmd(cmd)

    if modality == 'dwi':
        atlas_brain = None
        lv_mask = None
    return (labels, atlas, atlas_mask, atlas_brain, lv_mask)


def worker_wrapper((f, args, kwargs)):
    # allows us to wrap the per-subject module and remap the arguments
    # so that we can take lists of args since f in this case can be
    # ndmg_dwi_pipeline or ndmg_func_pipeline, and each takes slightly
    # different arguments
    return f(*args, **kwargs)


def session_level(inDir, outDir, subjs, sesh=None, task=None, run=None,
                  debug=False, modality='dwi', nproc=1, big=False,
                  stc=None):
    """
    Crawls the given BIDS organized directory for data pertaining to the given
    subject and session, and passes necessary files to ndmg_dwi_pipeline for
    processing.
    """
    labels, atlas, atlas_mask, atlas_brain, lv_mask = get_atlas(atlas_dir,
                                                                modality)
    mgu.execute_cmd("mkdir -p {} {}/tmp".format(outDir, outDir))

    result = sweep_directory(inDir, subjs, sesh, task, run, modality=modality)

    kwargs = {'clean': (not debug)}  # our keyword arguments
    if modality == 'dwi':
        dwis, bvals, bvecs, anats = result
        assert(len(anats) == len(dwis))
        assert(len(bvecs) == len(dwis))
        assert(len(bvals) == len(dwis))
        args = [[dw, bval, bvec, anat, atlas, atlas_mask,
                 labels, outDir] for (dw, bval, bvec, anat)
                in zip(dwis, bvals, bvecs, anats)]
        f = ndmg_dwi_pipeline  # the function of choice
        kwargs['big'] = big
    else:
        funcs, anats = result
        assert(len(anats) == len(funcs))
        args = [[func, anat, atlas, atlas_brain, atlas_mask,
                 lv_mask, labels, outDir] for (func, anat) in
                zip(funcs, anats)]
        f = ndmg_func_pipeline
        kwargs['stc'] = stc
    # optional args stored in kwargs
    # use worker wrapper to call function f with args arg
    # and keyword args kwargs
    arg_list = [(f, arg, kwargs) for arg in args]
    p = Pool(processes=nproc)  # start nproc in parallel
    try:
        result = p.map(worker_wrapper, arg_list)  # run them
        p.close()
    except:
        p.close()
    finally:
        p.join()
    rmflds = []
    if modality == 'func' and not debug:
       rmflds += [os.path.join(outDir, 'func', modal) for modal in ['clean', 'preproc', 'registered']]
       rmflds += [os.path.join(outDir, 'anat')]
    if not big:
        rmflds += [os.path.join(outDir, 'func', 'voxel-timeseries')]
    if len(rmflds) > 0:
        cmd = "rm -rf {}".format(" ".join(rmflds))
        mgu.execute_cmd(cmd)


def group_level(inDir, outDir, dataset=None, atlas=None, minimal=False,
                log=False, hemispheres=False, dwi=True):
    """
    Crawls the output directory from ndmg and computes qc metrics on the
    derivatives produced
    """
    if modality == 'func':
        outDir += '/connectomes'

    outDir = op.join(outDir, 'qa', 'graphs')
    mgu.execute_cmd("mkdir -p {}".format(outDir))

    labels_used = next(os.walk(inDir))[1]

    if atlas is not None:
        labels_used = [atlas]

    for skip in skippers:
        if skip in labels_used:
            print("Skipping {} parcellation".format(skip))
            labels_used.remove(skip)
            continue

    for label in labels_used:
        print("Parcellation: {}".format(label))
        tmp_in = op.join(inDir, label)
        fs = [op.join(tmp_in, fl)
              for root, dirs, files in os.walk(tmp_in)
              for fl in files
              if fl.endswith(".graphml") or fl.endswith(".gpickle") or fl.endswith('edgelist')]
        tmp_out = op.join(outDir, label)
        mgu.execute_cmd("mkdir -p {}".format(tmp_out))
        try:
            compute_metrics(fs, tmp_out, label, modality=modality)
            outf = op.join(tmp_out, '{}_plot'.format(label))
            make_panel_plot(tmp_out, outf, dataset=dataset, atlas=label,
                            minimal=minimal, log=log, hemispheres=hemispheres,
                            modality=modality)
        except Exception as e:
            print("Failed group analysis for {} parcellation.".format(label))
            print(e)
            continue



def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from M3r Images.")
    parser.add_argument('bids_dir', help='The directory with the input dataset'
                        ' formatted according to the BIDS standard.')
    parser.add_argument('output_dir', help='The directory where the output '
                        'files should be stored. If you are running group '
                        'level analysis this folder should be prepopulated '
                        'with the results of the participant level analysis.')
    parser.add_argument('analysis_level', help='Level of the analysis that '
                        'will be performed. Multiple participant level '
                        'analyses can be run independently (in parallel) '
                        'using the same output_dir.',
                        choices=['participant', 'group'])
    parser.add_argument('modality', help='Modality of MRI scans that \
                        are being evaluated.', choices=['dwi', 'func'])
    parser.add_argument('--participant_label', help='The label(s) of the '
                        'participant(s) that should be analyzed. The label '
                        'corresponds to sub-<participant_label> from the BIDS '
                        'spec (so it does not include "sub-"). If this '
                        'parameter is not provided all subjects should be '
                        'analyzed. Multiple participants can be specified '
                        'with a space separated list.', nargs="+")
    parser.add_argument('--session_label', help='The label(s) of the '
                        'session that should be analyzed. The label '
                        'corresponds to ses-<participant_label> from the BIDS '
                        'spec (so it does not include "ses-"). If this '
                        'parameter is not provided all sessions should be '
                        'analyzed. Multiple sessions can be specified '
                        'with a space separated list.', nargs="+")
    parser.add_argument('--task_label', help='The label(s) of the task '
                        'that should be analyzed. The label corresponds to '
                        'task-<task_label> from the BIDS spec (so it does not '
                        'include "task-"). If this parameter is not provided '
                        'all tasks should be analyzed. Multiple tasks can be '
                        'specified with a space separated list.', nargs="+")
    parser.add_argument('--run_label', help='The label(s) of the run '
                        'that should be analyzed. The label corresponds to '
                        'run-<run_label> from the BIDS spec (so it does not '
                        'include "task-"). If this parameter is not provided '
                        'all runs should be analyzed. Multiple runs can be '
                        'specified with a space separated list.', nargs="+") 
    parser.add_argument('--bucket', action='store', help='The name of '
                        'an S3 bucket which holds BIDS organized data. You '
                        'must have built your bucket with credentials to the '
                        'S3 bucket you wish to access.')
    parser.add_argument('--remote_path', action='store', help='The path to '
                        'the data on your S3 bucket. The data will be '
                        'downloaded to the provided bids_dir on your machine.')
    parser.add_argument('--push_data', action='store_true', help='flag to '
                        'push derivatives back up to S3.', default=False)
    parser.add_argument('--dataset', action='store', help='The name of '
                        'the dataset you are perfoming QC on.')
    parser.add_argument('--atlas', action='store', help='The atlas '
                        'being analyzed in QC (if you only want one).')
    parser.add_argument('--minimal', action='store_true', help='Determines '
                        'whether to show a minimal or full set of plots.',
                        default=False)
    parser.add_argument('--hemispheres', action='store_true', help='Whether '
                        'or not to break degrees into hemispheres or not',
                        default=False)
    parser.add_argument('--log', action='store_true', help='Determines '
                        'axis scale for plotting.', default=False)
    parser.add_argument('--debug', action='store_true', help='flag to store '
                        'temp files along the path of processing.',
                        default=False)
    parser.add_argument('--big', action='store_true', help='Whether to produce '
                        'big graphs for DWI, or voxelwise timeseries for fMRI.',
                         default=False)
    parser.add_argument("--nproc", action="store", help="The number of "
                        "process to launch. Should be approximately "
                        "<min(ncpu*hyperthreads/cpu, maxram/10).", default=1,
                        type=int)
    parser.add_argument("--stc", action="store", help='A file for slice '
                        'timing correction. Options are a TR sequence file '
                        '(where each line is the shift in TRs), '
                        'up (ie, bottom to top), down (ie, top to bottom), '
                        'and interleaved.', default=None)

    result = parser.parse_args()

    inDir = result.bids_dir
    outDir = result.output_dir
    subj = result.participant_label
    sesh = result.session_label
    task = result.task_label
    run = result.run_label
    buck = result.bucket
    remo = result.remote_path
    push = result.push_data
    level = result.analysis_level
    stc = result.stc
    debug = result.debug
    modality = result.modality
    nproc = result.nproc
    big = (True if result.big else False)

    minimal = result.minimal
    log = result.log
    atlas = result.atlas
    dataset = result.dataset
    hemi = result.hemispheres

    creds = bool(os.getenv("AWS_ACCESS_KEY_ID", 0) and
                 os.getenv("AWS_SECRET_ACCESS_KEY", 0))

    if level == 'participant':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if subj is not None:
                [s3_get_data(buck, remo, inDir, s, True) for s in subj]
            else:
                s3_get_data(buck, remo, inDir, public=creds)
        modif = 'ndmg_{}'.format(ndmg.version.replace('.', '-'))
        session_level(inDir, outDir, subj, sesh, task, run, debug,
                      modality, nproc, big, stc)

    elif level == 'group':
        if modality == 'func':
            gpath = op.join('func', 'connectomes')
        else:
            gpath = 'graphs'
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if atlas is not None:
                tpath = op.join(remo, gpath, atlas)
                tindir = op.join(outDir, gpath, atlas)
                # Using outDir as input location for group level since i work on graphs
            else:
                tpath = op.join(remo, gpath)
                tindir = op.join(outDir, gpath)
            s3_get_data(buck, tpath, tindir, public=creds)
        modif = 'qa'
        group_level(op.join(outDir, gpath), outDir, dataset, atlas, minimal, log, hemi)


    if push and buck is not None and remo is not None:
        print("Pushing results to S3...")
        s3_push_data(buck, remo, outDir, modif, creds)


if __name__ == "__main__":
    main()
