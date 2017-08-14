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

# ndmg_func_pipeline.py
# Created by Eric Bridgeford on 2016-06-07.
# Edited by Greg Kiar on 2017-03-14.
# Email: gkiar@jhu.edu, ebridge2@jhu.edu

import numpy as np
import nibabel as nb
import os.path as op
from argparse import ArgumentParser
from datetime import datetime
from ndmg.utils import utils as mgu
from ndmg import epi_register as mgreg
from ndmg import graph as mgg
from ndmg.timeseries import timeseries as mgts
from ndmg.stats.qa_func import qa_func
from ndmg.preproc import preproc_func as mgfp
from ndmg.preproc import preproc_anat as mgap
from ndmg.nuis import nuis as mgn
from ndmg.stats.qa_reg import *
import traceback


def ndmg_func_worker(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                     labels, outdir, clean=False, stc=None, fmt='gpickle'):
    """
    analyzes fmri images and produces subject-specific derivatives.

    **positional arguments:**
        func:
            - the path to a 4d (fmri) image.
        t1w:
            - the path to a 3d (anatomical) image.
        atlas:
            - the path to a reference atlas.
        atlas_brain:
            - the path to a reference atlas, brain extracted.
        atlas_mask:
            - the path to a reference brain mask.
        lv_mask:
            - the path to the lateral ventricles mask.
        labels:
            - a list of labels files.
        stc:
            - a slice timing correction file. see slice_time_correct() in the
              preprocessing module for details.
        outdir:
            - the base output directory to place outputs.
        clean:
            - a flag whether or not to clean out directories once finished.
        fmt:
            - the format for produced connectomes. supported options are
              gpickle and graphml.
    """
    startTime = datetime.now()

    # Create derivative output directories
    func_name = mgu.get_filename(func)
    t1w_name = mgu.get_filename(t1w)
    atlas_name = mgu.get_filename(atlas)

    paths = {'f_prep': "reg/func/preproc",
             'a_prep': "reg/t1w/preproc",
             'sreg_f': "reg/func/align/self",
             'sreg_a': "reg/t1w/align/self",
             'treg_f': "reg/func/align/template",
             'treg_a': "reg/t1w/align/template",
             'nuis': "nuis",
             'ts_voxel': "timeseries/voxel",
             'ts_roi': "timeseries/roi"}
    finals = {'ts_roi': paths['ts_roi'],
              'ts_voxel': paths['ts_voxel'],
              'conn': "connectomes"}

    tmpdir = '{}/tmp/{}'.format(outdir, func_name)
    qadir = "{}/qa/{}".format(outdir, func_name)

    tmp_dirs = {}
    qa_dirs = {}
    for (key, value) in (paths).iteritems():
        tmp_dirs[key] = "{}/{}".format(tmpdir, paths[key])
        qa_dirs[key] = "{}/{}".format(qadir, paths[key])
    qc_stats = "{}/{}_stats.pkl".format(qadir, func_name)

    final_dirs = {}
    for (key, value) in finals.iteritems():
        final_dirs[key] = "{}/{}".format(outdir, finals[key])

    cmd = "mkdir -p {} {} {}".format(" ".join(tmp_dirs.values()),
                                     " ".join(qa_dirs.values()),
                                     " ".join(final_dirs.values()))
    mgu.execute_cmd(cmd)

    # Graphs are different because of multiple parcellations
    if isinstance(labels, list):
        label_name = [mgu.get_filename(x) for x in labels]
        for label in label_name:
            cmd = "mkdir -p {}/{} {}/{} {}/{}"
            cmd = cmd.format(final_dirs['ts_roi'], label, final_dirs['conn'],
                             label, qa_dirs['ts_roi'], label)
            mgu.execute_cmd(cmd)
    else:
        label_name = mgu.get_filename(labels)
        label = label_name
        cmd = "mkdir -p {}/{} {}/{} {}/{}"
        cmd = cmd.format(final_dirs['ts_roi'], label, final_dirs['conn'],
                         label, qa_dirs['ts_roi'], label)
        mgu.execute_cmd(cmd)

    # Create derivative output file names
    preproc_func = "{}/{}_preproc.nii.gz".format(tmp_dirs['f_prep'], func_name)
    preproc_t1w_brain = "{}/{}_preproc_brain.nii.gz".format(tmp_dirs['a_prep'],
                                                            t1w_name)
    aligned_func = "{}/{}_aligned.nii.gz".format(tmp_dirs['treg_f'], func_name)
    aligned_t1w = "{}/{}_aligned.nii.gz".format(tmp_dirs['treg_a'], t1w_name)
    motion_func = "{}/{}_mc.nii.gz".format(tmp_dirs['f_prep'], func_name)
    nuis_func = "{}/{}_nuis.nii.gz".format(tmp_dirs['nuis'], func_name)
    voxel_ts = "{}/timeseries/voxel/{}_voxel.npz".format(outdir, func_name)

    print("This pipeline will produce the following derivatives...")
    print("fMRI volumes preprocessed: {}".format(preproc_func))
    print("fMRI volumes motion corrected: {}".format(motion_func))
    print("fMRI volume registered to atlas: {}".format(aligned_func))
    print("Voxel timecourse in atlas space: {}".format(voxel_ts))

    # Again, connectomes are different
    connectomes = ["{}/connectomes/{}/{}_{}.{}".format(outdir, x, func_name,
                                                       x, fmt)
                   for x in label_name]
    roi_ts = ["{}/{}/{}_{}.npz".format(final_dirs['ts_roi'], x, func_name, x)
              for x in label_name]
    print("ROI timeseries downsampled to given labels: " +
          ", ".join([x for x in roi_ts]))
    print("Connectomes downsampled to given labels: " +
          ", ".join([x for x in connectomes]))

    qc_func = qa_func()  # for quality control
    # Align fMRI volumes to Atlas
    # -------- Preprocessing Steps --------------------------------- #
    print "Preprocessing volumes..."
    f_prep = mgfp(func, preproc_func, motion_func, tmp_dirs['f_prep'])
    f_prep.preprocess(stc=stc)
    qc_func.func_preproc_qa(f_prep, qa_dirs['f_prep'])

    a_prep = mgap(t1w, preproc_t1w_brain, tmp_dirs['a_prep'])
    a_prep.preprocess()
    qc_func.anat_preproc_qa(a_prep, qa_dirs['a_prep'])

    # ------- Alignment Steps -------------------------------------- #
    print "Aligning volumes..."
    func_reg = mgreg(preproc_func, t1w, preproc_t1w_brain,
                     atlas, atlas_brain, atlas_mask, aligned_func,
                     aligned_t1w, tmp_dirs)
    func_reg.self_align()
    qc_func.self_reg_qa(func_reg, qa_dirs)
    func_reg.template_align()
    qc_func.temp_reg_qa(func_reg, qa_dirs)

    # ------- Nuisance Correction Steps ---------------------------- #
    print "Correcting Nuisance Variables..."
    nuis = mgn(aligned_func, aligned_t1w, nuis_func, tmp_dirs['nuis'],
               lv_mask=lv_mask, mc_params=f_prep.mc_params)
    nuis.nuis_correct()

    qc_func.nuisance_qa(nuis, qa_dirs['nuis'])

    # ------ Voxelwise Timeseries Steps ---------------------------- #
    print "Extracting Voxelwise Timeseries..."
    voxel = mgts().voxel_timeseries(nuis_func, atlas_mask, voxel_ts)
    qc_func.voxel_ts_qa(voxel, nuis_func, atlas_mask,
                        qcdir=qa_dirs['ts_voxel'])

    # ------ ROI Timeseries Steps ---------------------------------- #
    for idx, label in enumerate(label_name):
        print "Extracting ROI timeseries for " + label + " parcellation..."
        ts = mgts().roi_timeseries(nuis_func, labels[idx], roi_ts[idx])
        labeldir = "{}/{}".format(qa_dirs['ts_roi'], label)
        connectome = mgg(ts.shape[0], labels[idx], sens="func")
        connectome.cor_graph(ts)
        connectome.summary()
        connectome.save_graph(connectomes[idx], fmt=fmt)
        qc_func.roi_ts_qa(roi_ts[idx], aligned_func, aligned_t1w,
                          labels[idx], labeldir)
    # save our statistics so that we can do group level
    qc_func.save(qc_stats)

    print("Execution took: {}".format(datetime.now() - startTime))
    if clean:
        cmd = "rm -rf {}".format(tmpdir)
        mgu.execute_cmd(cmd)
    print("Complete!")


def ndmg_func_pipeline(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                       labels, outdir, clean=False, stc=None, fmt='gpickle'):
    """
    analyzes fmri images and produces subject-specific derivatives.

    **positional arguments:**
        func:
            - the path to a 4d (fmri) image.
        t1w:
            - the path to a 3d (anatomical) image.
        atlas:
            - the path to a reference atlas.
        atlas_brain:
            - the path to a reference atlas, brain extracted.
        atlas_mask:
            - the path to a reference brain mask.
        lv_mask:
            - the path to the lateral ventricles mask.
        labels:
            - a list of labels files.
        stc:
            - a slice timing correction file. see slice_time_correct() in the
              preprocessing module for details.
        outdir:
            - the base output directory to place outputs.
        clean:
            - a flag whether or not to clean out directories once finished.
        fmt:
            - the format for produced . supported options are gpickle and
            graphml.
    """
    try:
        ndmg_func_worker(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                         labels, outdir, clean=clean, stc=stc, fmt=fmt)
    except Exception, e:
        print(traceback.format_exc())
        return 
    return


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome"
                            " estimation pipeline from sMRI and DTI images")
    parser.add_argument("func", action="store", help="Nifti fMRI 4d EPI.")
    parser.add_argument("t1w", action="store", help="Nifti aMRI T1w image.")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("atlas_brain", action="store", help="Nifti T1 MRI"
                        " brain only atlas")
    parser.add_argument("atlas_mask", action="store", help="Nifti binary mask"
                        " of brain space in the atlas")
    parser.add_argument("lv_mask", action="store", help="Nifti binary mask of"
                        " lateral ventricles in atlas space.")
    parser.add_argument("outdir", action="store", help="Path to which"
                        " derivatives will be stored")
    parser.add_argument("stc", action="store", help="A file or setting for"
                        " slice timing correction. If file option selected,"
                        " must provide path as well.",
                        choices=["none", "interleaved", "up", "down", "file"])
    parser.add_argument("labels", action="store", nargs="*", help="Nifti"
                        " labels of regions of interest in atlas space")
    parser.add_argument("-s", "--stc_file", action="store",
                        help="File for STC.")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-f", "--fmt", action="store", default='gpickle',
                        help="Determines connectome output format")
    result = parser.parse_args()

    result.stc = None if result.stc == "none" else result.stc

    if result.stc == "file":
        if result.stc_file is None:
            sys.exit("Selected 'file' option for slice timing correction but"
                     " did not pass a file. Please select another option or"
                     " provide a file.")
        else:
            if not op.isfile(result.stc_file):
                sys.exit("Invalid file for STC provided.")
            else:
                result.stc = result.stc_file

    # Create output directory
    print "Creating output directory: {}".format(result.outdir)
    print "Creating output temp directory: {}/tmp".format(result.outdir)
    mgu.execute_cmd("mkdir -p {} {}/tmp".format(result.outdir, result.outdir))

    ndmg_func_pipeline(result.func, result.t1w, result.atlas,
                       result.atlas_brain, result.atlas_mask,
                       result.lv_mask, result.labels, result.outdir,
                       result.clean, result.stc, result.fmt)

if __name__ == "__main__":
    main()
