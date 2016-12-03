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
from ndmg import register as mgr
from ndmg import graph as mgg
import numpy as np
import nibabel as nb
from ndmg.timeseries import timeseries as mgts
from ndmg.stats import fmri_qc as mgqc
from ndmg.preproc import preproc_fmri as mgp
from ndmg.nuis import nuis as mgn
from ndmg.stats import qc as mggqc



def fngs_pipeline(fmri, struct, an, atlas, atlas_brain, atlas_mask, lv_mask,
                  labels, outdir, clean=False, stc=None, fmt='gpickle'):
    """
    Analyzes fMRI images and produces subject-specific derivatives.

    **Positional Arguments:**
        fmri:
            - the path to a 4D (fMRI) image.
        struct:
            - the path to a 3d (anatomical) image.
        an:
            - an integer indicating the type of anatomical image.
              (1 for T1w, 2 for T2w, 3 for PD).
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

    print "here"
    print stc
    # Create derivative output directories
    fmri_name = op.splitext(op.splitext(op.basename(fmri))[0])[0]
    struct_name = op.splitext(op.splitext(op.basename(struct))[0])[0]
    atlas_name = op.splitext(op.splitext(op.basename(atlas))[0])[0]

    qcdir = outdir + "/qc"
    mcdir = qcdir + "/mc/" + fmri_name
    regdir = qcdir + "/reg/" + fmri_name
    overalldir = qcdir + "/overall/" + fmri_name
    roidir = qcdir + "/roi/" + fmri_name
    nuisdir = qcdir + "/nuis/" + fmri_name

    cmd = "mkdir -p " + outdir + "/reg_fmri " + outdir +\
        "/preproc_fmri " + outdir + "/motion_fmri " + outdir +\
        "/voxel_timeseries " + outdir + "/roi_timeseries " +\
        outdir + "/reg_struct " + outdir + "/tmp " +\
        outdir + "/connectomes " + outdir + "/nuis_fmri " + qcdir + " " +\
        mcdir + " " + regdir + " " + overalldir + " " + roidir + " " + nuisdir
    mgu().execute_cmd(cmd)

    qc_html = overalldir + "/" + fmri_name + ".html"

    mggqc().generate_html_templated(qc_html)

    # Graphs are different because of multiple atlases
    if isinstance(labels, list):
        label_name = [op.splitext(op.splitext(op.basename(x))[0])[0]
                      for x in labels]
        for label in label_name:
            p = Popen("mkdir -p " + outdir + "/roi_timeseries/" + label,
                      stdout=PIPE, stderr=PIPE, shell=True)
            p = Popen("mkdir -p " + outdir + "/connectomes/" + label,
                      stdout=PIPE, stderr=PIPE, shell=True)
    else:
        label_name = op.splitext(op.splitext(op.basename(labels))[0])[0]
        p = Popen("mkdir -p " + outdir + "/roi_timeseries/" + label_name,
                  stdout=PIPE, stderr=PIPE, shell=True)
        p = Popen("mkdir -p " + outdir + "/connectomes/" + label_name,
                  stdout=PIPE, stderr=PIPE, shell=True)

    # Create derivative output file names
    preproc_fmri = outdir + "/preproc_fmri/" + fmri_name + "_preproc.nii.gz"
    aligned_fmri = outdir + "/reg_fmri/" + fmri_name + "_aligned.nii.gz"
    aligned_struct = outdir + "/reg_struct/" + fmri_name +\
        "_anat_aligned.nii.gz"
    motion_fmri = outdir + "/motion_fmri/" + fmri_name + "_mc.nii.gz"
    nuis_fmri = outdir + "/nuis_fmri/" + fmri_name + "_nuis.nii.gz"
    voxel_ts = outdir + "/voxel_timeseries/" + fmri_name + "_voxel.npz"

    print "This pipeline will produce the following derivatives..."
    print "fMRI volumes preprocessed: " + preproc_fmri
    print "fMRI volumes motion corrected: " + motion_fmri
    print "fMRI volume registered to atlas: " + aligned_fmri
    print "Voxel timecourse in atlas space: " + voxel_ts
    print "Quality Control HTML Page: " + qc_html
    # Again, connectomes are different
    connectomes = [outdir + "/connectomes/" + x + '/' + fmri_name +
              "_" + x + '.' + fmt for x in label_name]
    roi_ts = [outdir + "/roi_timeseries/" + x + '/' + fmri_name + "_" + x +
              ".npz" for x in label_name]
    print "ROI timecourse downsampled to given labels: " +\
          (", ".join([x for x in roi_ts]))

    # Align fMRI volumes to Atlas
    print "Preprocessing volumes..."
    mgp().preprocess(fmri, preproc_fmri, motion_fmri, outdir,
                     qcdir=mcdir, stc=stc)
    print "Aligning volumes..."
    mgr().fmri2atlas(preproc_fmri, struct, atlas, atlas_brain, atlas_mask,
                     aligned_fmri, aligned_struct, outdir,
                     qcdir=regdir)
    print "Correcting Nuisance Variables..."
    mgn().nuis_correct(aligned_fmri, aligned_struct, atlas_mask, an, lv_mask,
                       nuis_fmri, outdir, qcdir=nuisdir)
    print "Extracting Voxelwise Timeseries..."
    voxel = mgts().voxel_timeseries(nuis_fmri, atlas_mask, voxel_ts)
    mgqc().stat_summary(aligned_fmri, fmri, motion_fmri, atlas_mask, voxel,
                        aligned_struct, atlas_brain,
                        qcdir=overalldir, scanid=fmri_name, qc_html=qc_html)
    for idx, label in enumerate(label_name):
        print "Extracting ROI timeseries for " + label + " parcellation..."
        try:
            ts = mgts().roi_timeseries(nuis_fmri, labels[idx], roi_ts[idx],
                                   qcdir=roidir,
                                   scanid=fmri_name, refid=label)
            mggqc().image_align(atlas_brain, labels[idx], roidir, scanid=atlas_name,
                               refid=label)
        except OSError as err:
            print(err)
        connectome = mgg(ts.shape[0], labels[idx], sens="Functional")
        connectome.cor_graph(ts)
        connectome.summary()
        connectome.save_graph(connectomes[idx], fmt=fmt)

    #cmd = "rm -r " + outdir + "/tmp/" + fmri_name + "*"
    #mgu().execute_cmd(cmd)

    print "Complete! FNGS first run"
    pass


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("fmri", action="store", help="Nifti fMRI stack")
    parser.add_argument("struct", action="store", help="Nifti aMRI")
    parser.add_argument("an", action="store", help="anatomical image type. \
                        1 for T1w (default), 2 for T2w, 3 for PD.", default=1)
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("atlas_brain", action="store", help="Nifti T1 MRI \
                        brain only atlas")
    parser.add_argument("atlas_mask", action="store", help="Nifti binary mask of \
                        brain space in the atlas")
    parser.add_argument("lv_mask", action="store", help="Nifti binary mask of \
                        lateral ventricles in atlas space.")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-s", "--stc", action="store", help="A file for slice timing \
                        correction. Options are a TR sequence file (where \
                        each line is the shift in TRs), up (ie, bottom to top), \
                        down (ie, top to bottom), and interleaved.", default=None)
    parser.add_argument("-f", "--fmt", action="store", default='gpickle',
                        help="Determines connectome output format")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p " + result.outdir + " " + result.outdir + "/tmp"
    print "Creating output directory: " + result.outdir
    print "Creating output temp directory: " + result.outdir + "/tmp"
    mgu().execute_cmd(cmd)

    fngs_pipeline(result.fmri, result.struct, int(result.an), result.atlas,
                  result.atlas_brain, result.atlas_mask, result.lv_mask,
                  result.labels, result.outdir, result.clean, result.stc,
                  result.fmt)


if __name__ == "__main__":
    main()
