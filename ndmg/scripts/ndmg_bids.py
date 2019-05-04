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

# ndmg_bids.py
# Repackaged and maintained by Derek Pisner and Eric Bridgeford 2019
# Email: dpisner@utexas.edu
# Originally created by Greg Kiar on 2016-07-25.
# edited by Eric Bridgeford to incorporate fMRI, multi-threading, and
# big-graph generation.

import warnings

warnings.simplefilter("ignore")
from ndmg.scripts.ndmg_dwi_pipeline import ndmg_dwi_pipeline, ndmg_dwi_worker
from ndmg.scripts.ndmg_func_pipeline import ndmg_func_pipeline
from ndmg.utils.bids_utils import *
from ndmg.stats.qa_graphs import *
from ndmg.stats.qa_graphs_plotting import *
from glob import glob
from ndmg.utils import gen_utils as mgu
import ndmg
import os.path as op
import glob
import os
import shutil
import sys
from multiprocessing import Pool
from ndmg.scripts import ndmg_cloud as nc

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
skippers = ['slab907', 'slab1068', 'DS01216', 'DS01876',
            'DS03231', 'DS06481', 'DS16784', 'DS72784',
            'hemispheric_res-1x1x1', 'hemispheric_res-2x2x2',
            'tissue_res-1x1x1', 'tissue_res-2x2x2']


def get_atlas(atlas_dir, modality, vox_size):
    """
    Given the desired location for atlases and the type of processing, ensure
    we have all the atlases and parcellations.
    """
    if vox_size == '2mm':
        dims = '2x2x2'
    elif vox_size == '1mm':
        dims = '1x1x1'
    else:
        raise ValueError('Voxel dimensions of input t1w image not currently supported by ndmg.')

    if modality == 'dwi':
	atlas = op.join(atlas_dir, 'reference_brains/MNI152NLin6_res-' + dims + '_T1w.nii.gz')
	atlas_mask = op.join(atlas_dir, 'mask/MNI152NLin6_res-' + dims + '_T1w_descr-brainmask.nii.gz')
	labels = [i for i in glob.glob(atlas_dir + '/label/Human/*.nii.gz') if dims in i]
	labels = [op.join(atlas_dir, 'label/Human/', l) for l in labels]
	fils = labels + [atlas, atlas_mask]
    if modality == 'func':
        atlas = op.join(atlas_dir, 'atlas/MNI152NLin6_res-' + dims + '_T1w.nii.gz')
        atlas_brain = op.join(atlas_dir, 'atlas/' +
                              'MNI152NLin6_res-' + dims + '_T1w_brain.nii.gz')
        atlas_mask = op.join(atlas_dir,
                             'mask/MNI152NLin6_res-' + dims + '_T1w_brainmask.nii.gz')
        lv_mask = op.join(atlas_dir, "mask/HarvardOxford_variant-" +
                          "lateral-ventricles-thr25" +
                          "_res-' + dims + '_brainmask.nii.gz")

        labels = [i for i in glob.glob(atlas_dir + '/label/*.nii.gz') if dims in i]
        labels = [op.join(atlas_dir, 'label', l) for l in labels]
        fils = labels + [atlas, atlas_mask, atlas_brain, lv_mask]

    ope = op.exists
    for f in fils:
        if not ope(f):
            print(f)
    if any(not ope(f) for f in fils):
        print("Cannot find atlas information; downloading...")
        mgu.execute_cmd('mkdir -p ' + atlas_dir)
        cmd = 'wget https://github.com/neurodata/neuroparc/archive/master.zip'
        os.system(cmd)
        cmd = 'unzip /master.zip'
        os.system(cmd)
        os.rename('/neuroparc-master/atlases', '/ndmg_atlases')
        shutil.rmtree('/neuroparc-master')
        os.remove('master.zip')

    if modality == 'dwi':
        atlas_brain = None
        lv_mask = None
    return (labels, atlas, atlas_mask, atlas_brain, lv_mask)


def worker_wrapper(xxx_todo_changeme):
    # allows us to wrap the per-subject module and remap the arguments
    # so that we can take lists of args since f in this case can be
    # ndmg_dwi_pipeline or ndmg_func_pipeline, and each takes slightly
    # different arguments
    (f, args, kwargs) = xxx_todo_changeme
    return f(*args, **kwargs)


def session_level(inDir, outDir, subjs, vox_size, big, clean, stc, atlas_select, mod_type, track_type, mod_func,
                  reg_style, sesh=None, task=None, run=None, debug=False, modality='dwi', nproc=1):
    """
    Crawls the given BIDS organized directory for data pertaining to the given
    subject and session, and passes necessary files to ndmg_dwi_pipeline for
    processing.
    """

    labels, atlas, atlas_mask, atlas_brain, lv_mask = get_atlas(atlas_dir,
                                                                modality, vox_size)

    if atlas_select:
        labels = [i for i in labels if atlas_select in i]
    # mgu.execute_cmd("mkdir -p {} {}/tmp".format(outDir, outDir))

    result = sweep_directory(inDir, subjs, sesh, task, run, modality)

    if modality == 'dwi':
        dwis, bvals, bvecs, anats = result
        assert (len(anats) == len(dwis))
        assert (len(bvecs) == len(dwis))
        assert (len(bvals) == len(dwis))
        args = [[dw, bval, bvec, anat, atlas, atlas_mask,
                 labels, "%s%s%s%s%s" % (
                     outDir, '/sub', bval.split('sub')[1].split('/')[0], '/ses', bval.split('ses')[1].split('/')[0])]
                for
                (dw, bval, bvec, anat)
                in zip(dwis, bvals, bvecs, anats)]
    else:
        funcs, anats = result
        assert (len(anats) == len(funcs))
        args = [[func, anat, atlas, atlas_brain, atlas_mask,
                 lv_mask, labels, outDir] for (func, anat) in
                zip(funcs, anats)]

    # optional args stored in kwargs
    # use worker wrapper to call function f with args arg
    # and keyword args kwargs
    ndmg_dwi_worker(args[0][0], args[0][1], args[0][2], args[0][3], atlas, atlas_mask, labels, outDir, vox_size, mod_type, track_type, mod_func, reg_style, clean, big)
    rmflds = []
    if modality == 'func' and not debug:
        rmflds += [os.path.join(outDir, 'func', modal) for modal in ['clean', 'preproc', 'registered']]
        rmflds += [os.path.join(outDir, 'anat')]
    if not big:
        rmflds += [os.path.join(outDir, 'func', 'voxel-timeseries')]
    if len(rmflds) > 0:
        cmd = "rm -rf {}".format(" ".join(rmflds))
        mgu.execute_cmd(cmd)
    sys.exit(0)  # terminated


def group_level(inDir, outDir, vox_size, big, clean, stc, dataset=None, atlas=None, minimal=False,
                log=False, hemispheres=False, modality='dwi'):
    """
    Crawls the output directory from ndmg and computes qc metrics on the
    derivatives produced
    """
    outDir = op.join(outDir, 'qa', 'roi-connectomes')
    mgu.execute_cmd("mkdir -p {}".format(outDir))
    labels_used = next(os.walk(inDir))[1]

    if atlas is not None:
        labels_used = [atlas]

    for skip in skippers:
        if skip in labels_used:
            print(("Skipping {} parcellation".format(skip)))
            labels_used.remove(skip)
            continue

    gfmt = '_elist.csv' if modality == 'dwi' else '_adj.csv'
    for label in labels_used:
        print(("Parcellation: {}".format(label)))
        tmp_in = op.join(inDir, label)
        fs = [op.join(tmp_in, fl)
              for root, dirs, files in os.walk(tmp_in)
              for fl in files
              if fl.endswith(gfmt)]
        tmp_out = op.join(outDir, label)
        mgu.execute_cmd("mkdir -p {}".format(tmp_out))
        try:
            compute_metrics(fs, tmp_out, label, modality=modality)
            outf = op.join(tmp_out, '{}_plot'.format(label))
            make_panel_plot(tmp_out, outf, dataset=dataset, atlas=label,
                            minimal=minimal, log=log, hemispheres=hemispheres,
                            modality=modality)
        except Exception as e:
            print(("Failed group analysis for {} parcellation.".format(label)))
            print(e)
            continue
    sys.exit(0)


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
                        choices=['participant', 'group'], default='participant')
    parser.add_argument('--modality', help='Modality of MRI scans that \
                        are being evaluated.', choices=['dwi', 'func'], default='dwi')
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
                                                        'being analyzed in QC (if you only want one).', default=None)
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
    parser.add_argument('--big', action='store_true',
                        help='Whether to produce \
                        big graphs for DWI, or voxelwise timeseries for fMRI.',
                        default=False)
    parser.add_argument("--vox", action="store", default='2mm',
                        help="Voxel size to use for template registrations \
                        (e.g. default is '2mm')")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("--nproc", action="store", help="The number of "
                                                        "process to launch. Should be approximately "
                                                        "<min(ncpu*hyperthreads/cpu, maxram/10).", default=1,
                        type=int)
    parser.add_argument("--stc", action="store", help='A file for slice '
                                                      'timing correction. Options are a TR sequence file '
                                                      '(where each line is the shift in TRs), '
                                                      'up (ie, bottom to top), down (ie, top to bottom), '
                                                      'or interleaved.', default=None)
    parser.add_argument("--mod", action="store",
                        help='Determinstic (det) or probabilistic (prob) tracking. Default is det.', default='det')
    parser.add_argument("--tt", action="store", help='Tracking approach: eudx or local. Default is eudx.',
                        default='eudx')
    parser.add_argument("--mf", action="store", help='Diffusion model: csd, csa, or tensor. Default is tensor.',
                        default='tensor')
    parser.add_argument("--sp", action="store", help='Space for tractography. Default is native.', default='native')
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
    big = result.big
    clean = result.clean
    vox_size = result.vox
    minimal = result.minimal
    log = result.log
    atlas_select = result.atlas
    dataset = result.dataset
    hemi = result.hemispheres
    mod_type = result.mod
    track_type = result.tt
    mod_func = result.mf
    reg_style = result.sp

    creds = bool(os.getenv("AWS_ACCESS_KEY_ID", 0) and
                 os.getenv("AWS_SECRET_ACCESS_KEY", 0))

    if level == 'participant':
        if buck is not None and remo is not None:
            print("Retrieving data from S3...")
            if subj is not None:
                print(buck)
                print(remo)
                print(inDir)
                [nc.s3_get_data(buck, remo, inDir) for s in subj]
            else:
                nc.s3_get_data(buck, remo, inDir, public=creds)
        modif = 'ndmg_{}'.format(ndmg.version.replace('.', '-'))
        session_level(inDir, outDir, subj, vox_size, big, clean, stc,
                      atlas_select, mod_type, track_type, mod_func, reg_style, sesh, task, run,
                      debug, modality, nproc)

    # elif level == 'group':
    #     gpath = op.join(inDir, modality, 'roi-connectomes')
    #     if buck is not None and remo is not None:
    #         print("Retrieving data from S3...")
    #         if atlas is not None:
    #             tpath = op.join(remo, gpath, atlas)
    #             tindir = op.join(outDir, gpath, atlas)
    #             # Using outDir as input location for group level since
    #         else:
    #             tpath = op.join(remo, gpath)
    #             tindir = op.join(outDir, gpath)
    #         nc.s3_get_data(buck, tpath, tindir, public=creds)
    #     modif = 'qa'
    #     group_level(op.join(inDir, gpath), outDir, vox_size, big, clean, stc,
    #                 dataset, atlas, minimal, log, hemi, modality)

    if push and buck is not None and remo is not None:
        print("Pushing results to S3...")
        nc.s3_push_data(buck, remo, outDir, modif, creds)


if __name__ == "__main__":
    main()
