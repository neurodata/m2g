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

# fmri_pipeline.py
# Created by Eric Bridgeford on 2016-06-07.
# Email: gkiar@jhu.edu, wgr@jhu.edu, ebridge2@jhu.edu

from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE
import os.path as op
from ndmg.utils import utils as mgu
from ndmg.register import register as mgr
from ndmg.graph import graph as mgg
import numpy as np
import nibabel as nb
from ndmg.timeseries import timeseries as mgts
from ndmg.qc import qc as mgqc
from ndmg.preproc import preproc as mgp
from ndmg.nuis import nuis as mgn
from guppy import hpy


def fmri_pipeline(fmri, mprage, atlas, atlas_brain, mask, labels, outdir,
                  clean=False, fmt='gpickle'):
    """
    Creates a brain graph from MRI data
    """
    startTime = datetime.now()

    # Create derivative output directories
    fmri_name = op.splitext(op.splitext(op.basename(fmri))[0])[0]
    mprage_name = op.splitext(op.splitext(op.basename(mprage))[0])[0]
    atlas_name = op.splitext(op.splitext(op.basename(atlas))[0])[0]

    qcdir = outdir + "/qc"
    mcdir = qcdir + "/mc/" + fmri_name
    regdir = qcdir + "/reg/" + fmri_name
    overalldir = qcdir + "/overall/" + fmri_name
    roidir = qcdir + "/roi/" + fmri_name

    cmd = "mkdir -p " + outdir + "/reg_fmri " + outdir +\
        "/preproc_fmri " + outdir + "/motion_fmri " + outdir +\
        "/voxel_timeseries " + outdir + "/roi_timeseries " +\
        outdir + "/reg_mprage " + outdir + "/tmp " +\
        outdir + "/graphs " + outdir + "/nuis_fmri " + qcdir + " " +\
        mcdir + " " + regdir + " " + overalldir + " " + roidir
    mgu().execute_cmd(cmd)

    # Graphs are different because of multiple atlases
    if isinstance(labels, list):
        label_name = [op.splitext(op.splitext(op.basename(x))[0])[0]
                      for x in labels]
        for label in label_name:
            p = Popen("mkdir -p " + outdir + "/roi_timeseries/" + label,
                      stdout=PIPE, stderr=PIPE, shell=True)
            p = Popen("mkdir -p " + outdir + "/graphs/" + label,
                      stdout=PIPE, stderr=PIPE, shell=True)
    else:
        label_name = op.splitext(op.splitext(op.basename(labels))[0])[0]
        p = Popen("mkdir -p " + outdir + "/roi_timeseries/" + label_name,
                  stdout=PIPE, stderr=PIPE, shell=True)
        p = Popen("mkdir -p " + outdir + "/graphs/" + label_name,
                  stdout=PIPE, stderr=PIPE, shell=True)

    # Create derivative output file names
    preproc_fmri = outdir + "/preproc_fmri/" + fmri_name + "_preproc.nii.gz"
    aligned_fmri = outdir + "/reg_fmri/" + fmri_name + "_aligned.nii.gz"
    aligned_mprage = outdir + "/reg_mprage/" + fmri_name +\
        "_anat_aligned.nii.gz"
    motion_fmri = outdir + "/motion_fmri/" + fmri_name + "_mc.nii.gz"
    nuis_fmri = outdir + "/nuis_fmri/" + fmri_name + "_nuis.nii.gz"
    voxel_ts = outdir + "/voxel_timeseries/" + fmri_name + "_voxel.npz"

    print "This pipeline will produce the following derivatives..."
    print "fMRI volumes preprocessed: " + preproc_fmri
    print "fMRI volumes motion corrected: " + motion_fmri
    print "fMRI volume registered to atlas: " + aligned_fmri
    print "Voxel timecourse in atlas space: " + voxel_ts

    # Again, graphs are different
    graphs = [outdir + "/graphs/" + x + '/' + fmri_name + "_" + x + '.' + fmt
              for x in label_name]
    roi_ts = [outdir + "/roi_timeseries/" + x + '/' + fmri_name + "_" + x +
              ".npz" for x in label_name]
    print "ROI timecourse downsampled to given labels: " +\
          (", ".join([x for x in roi_ts]))

    # Align fMRI volumes to Atlas
    print "Preprocessing volumes..."
    mgp().preprocess(fmri, preproc_fmri, motion_fmri, outdir, qcdir=mcdir)
    print "Aligning volumes..."
    mgr().fmri2atlas(preproc_fmri, mprage, atlas, atlas_brain, mask,
                     aligned_fmri, aligned_mprage, outdir, qcdir=regdir)
    #mgn().calc_residuals(aligned_fmri, nuis_fmri)
    mgu().execute_cmd("fslmaths  " + aligned_fmri + " -bptf 100 -1 " + nuis_fmri)
 
    voxel = mgts().voxel_timeseries(nuis_fmri, mask, voxel_ts)
    
    mgqc().stat_summary(nuis_fmri, fmri, motion_fmri, mask, voxel,
                        aligned_mprage, atlas_brain,
                        qcdir=overalldir, scanid=fmri_name)

    for idx, label in enumerate(label_name):
        print "Extracting roi timeseries for " + label + " parcellation..."
        try:
            ts = mgts().roi_timeseries(nuis_fmri, labels[idx], roi_ts[idx],
                                   qcdir=roidir,
                                   scanid=fmri_name, refid=label)
            mgqc().image_align(atlas_brain, labels[idx], roidir, scanid=atlas_name,
                               refid=label)
        except OSError as err:
            print(err)
        graph = mgg(ts.shape[0], labels[idx])
        graph.cor_graph(ts)
        graph.summary()
        graph.save_graph(graphs[idx], fmt=fmt)

    #cmd = "rm -r " + outdir + "/tmp/" + fmri_name + "*"
    #mgu().execute_cmd(cmd)

    print "Complete! FNGS first run"
    pass


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("fmri", action="store", help="Nifti DTI image stack")
    parser.add_argument("mprage", action="store", help="Nifti T1 MRI image")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("atlas_brain", action="store", help="Nifti T1 MRI \
                        brain only atlas")
    parser.add_argument("mask", action="store", help="Nifti binary mask of \
                        brain space in the atlas")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-f", "--fmt", action="store", default='gpickle',
                        help="Determines graph output format")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p " + result.outdir + " " + result.outdir + "/tmp"
    print "Creating output directory: " + result.outdir
    print "Creating output temp directory: " + result.outdir + "/tmp"
    mgu().execute_cmd(cmd)

    fmri_pipeline(result.fmri, result.mprage, result.atlas, result.atlas_brain,
                  result.mask, result.labels, result.outdir, result.clean,
                  result.fmt)


if __name__ == "__main__":
    main()
