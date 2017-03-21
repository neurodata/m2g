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
from ndmg import register as mgr
from ndmg import graph as mgg
from ndmg.timeseries import timeseries as mgts
from ndmg.stats import qa_func as mgrf
from ndmg.preproc import preproc_func as mgp
from ndmg.nuis import nuis as mgn
from ndmg.stats.qa_reg import *


def fngs_pipeline(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                  labels, outdir, clean=False, stc=None, fmt='gpickle'):
    """
    Analyzes fMRI images and produces subject-specific derivatives.

    **Positional Arguments:**
        func:
            - the path to a 4D (fMRI) image.
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
            - a slice timing correction file. See slice_time_correct() in the
              preprocessing module for details.
        outdir:
            - the base output directory to place outputs.
        clean:
            - a flag whether or not to clean out directories once finished.
        fmt:
            - the format for produced . Supported options are gpickle and
            graphml.
    """
    startTime = datetime.now()

    # Create derivative output directories
    func_name = mgu.get_filename(func)
    t1w_name = mgu.get_filename(t1w)
    atlas_name = mgu.get_filename(atlas)

    qadir = "{}/qa/{}".format(outdir, func_name)
    prepdir = "{}/reg/func/preproc".format(qadir)
    regfdir = "{}/reg/func/align".format(qadir)
    regadir = "{}/reg/t1w/align".format(qadir)
    roidir = "{}/ts_roi".format(qadir)
    voxeldir = "{}/ts_voxel".format(qadir)
    nuisdir = "{}/nuis".format(qadir)

    cmd = "mkdir -p {} {} {} {} {} {} {} {}/reg/func/align {}/reg/func/preproc \
           {}/reg/func/mc {}/ts_voxel {}/ts_roi {}/reg/t1w {}/tmp \
           {}/connectomes/ {}/nuis"
    cmd = cmd.format(qadir, prepdir, regfdir, regadir, roidir, voxeldir,
                     nuisdir, *([outdir] * 9))
    mgu.execute_cmd(cmd)

    # Graphs are different because of multiple parcellations
    if isinstance(labels, list):
        label_name = [mgu.get_filename(x) for x in labels]
        for label in label_name:
            cmd = "mkdir -p {}/ts_roi/{} {}/connectomes/{} {}/{}"
            cmd = cmd.format(outdir, label, outdir, label, roidir, label)
            mgu.execute_cmd(cmd)
    else:
        label_name = mgu.get_filename(labels)
        label = label_name
        cmd = "mkdir -p {}/ts_roi/{} {}/connectomes/{} {}/{}"
        cmd = cmd.format(outdir, label, outdir, label, roidir, label)
        mgu.execute_cmd(cmd)

    # Create derivative output file names
    preproc_func = "{}/reg/func/preproc/{}_preproc.nii.gz".format(outdir, func_name)
    aligned_func = "{}/reg/func/align/{}_aligned.nii.gz".format(outdir, func_name)
    aligned_t1w = "{}/reg/t1w/{}_aligned.nii.gz".format(outdir, t1w_name)
    motion_func = "{}/reg/func/mc/{}_mc.nii.gz".format(outdir, func_name)
    nuis_func = "{}/nuis/{}_nuis.nii.gz".format(outdir, func_name)
    voxel_ts = "{}/ts_voxel/{}_voxel.npz".format(outdir, func_name)

    print("This pipeline will produce the following derivatives...")
    print("fMRI volumes preprocessed: {}".format(preproc_func))
    print("fMRI volumes motion corrected: {}".format(motion_func))
    print("fMRI volume registered to atlas: {}".format(aligned_func))
    print("Voxel timecourse in atlas space: {}".format(voxel_ts))

    # Again, connectomes are different
    connectomes = ["{}/connectomes/{}/{}_{}.{}".format(outdir, x, func_name,
                                                       x, fmt)
                   for x in label_name]
    roi_ts = ["{}/ts_roi/{}/{}_{}.npy".format(outdir, x, func_name, x)
              for x in label_name] 
    print("ROI timeseries downsampled to given labels: " +
          ", ".join([x for x in roi_ts]))
    print("Connectomes downsampled to given labels: " +
          ", ".join([x for x in connectomes]))

    # Align fMRI volumes to Atlas
    print "Preprocessing volumes..."
    mgp().preprocess(func, preproc_func, motion_func, outdir, stc=stc)
    mgrf.preproc_qa(motion_func, prepdir)
    
    print "Aligning volumes..."
    mgr().func2atlas(preproc_func, t1w, atlas, atlas_brain, atlas_mask,
                     aligned_func, aligned_t1w, outdir)
    mgrf.reg_func_qa(aligned_func, atlas, qcdir=regfdir)
    mgrf.reg_anat_qa(aligned_t1w, atlas, qcdir=regadir)

    print "Correcting Nuisance Variables..."
    nuis = mgn().nuis_correct(aligned_func, nuis_func, lv_mask, trim=2)
    mgrf.nuisance_qa(nuis, nuis_func, aligned_func, qcdir=nuisdir)

    print "Extracting Voxelwise Timeseries..."
    voxel = mgts().voxel_timeseries(nuis_func, atlas_mask, voxel_ts)
    mgrf.voxel_ts_qa(voxel, nuis_func, atlas_mask, qcdir=voxeldir)

    for idx, label in enumerate(label_name):
        print "Extracting ROI timeseries for " + label + " parcellation..."
        ts = mgts().roi_timeseries(nuis_func, labels[idx], roi_ts[idx])
        labeldir = "{}/{}".format(roidir, label)
        connectome = mgg(ts.shape[0], labels[idx], sens="func")
        connectome.cor_graph(ts)
        connectome.summary()
        connectome.save_graph(connectomes[idx], fmt=fmt)
        mgrf.roi_ts_qa(roi_ts[idx], aligned_anat, labels[idx], labeldir)

    print("Execution took: {}".format(datetime.now() - startTime))

    if clean:
        cmd = "rm -r {}/tmp/{}*".format(outdir, func_name)
        mgu.execute_cmd(cmd)

    print("Complete!")


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome"
                            " estimation pipeline from sMRI and DTI images")
    parser.add_argument("func", action="store", help="Nifti fMRI stack")
    parser.add_argument("t1w", action="store", help="Nifti aMRI")
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

    fngs_pipeline(result.func, result.t1w, result.atlas,
                  result.atlas_brain, result.atlas_mask, result.lv_mask,
                  result.labels, result.outdir, result.clean, result.stc,
                  result.fmt)


if __name__ == "__main__":
    main()
