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
from ndmg.stats.qa_mri import qa_mri
from ndmg.preproc import preproc_func as mgfp
from ndmg.preproc import preproc_anat as mgap
from ndmg.nuis import nuis as mgn
from ndmg.stats.qa_reg import *
import traceback
from ndmg.utils.bids_utils import name_resource
import sys
import os


def ndmg_func_worker(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                     labels, outdir, clean=False, stc=None,
                     big=False):
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
        big:
            - whether to produce voxelwise timeseries.
    """
    startTime = datetime.now()
    fmt = '_adj.csv'
    namer = name_resource(func, t1w, atlas, outdir)

    paths = {'prep_m': "func/preproc",
             'prep_a': "anat/preproc",
             'reg_m': "func/registered",
             'reg_a': "anat/registered",
             'nuis_f': "func/clean",
             'nuis_a': "func/clean",
             'ts_voxel': "func/voxel-timeseries",
             'ts_roi': "func/roi-timeseries",
             'conn': "func/roi-connectomes"}

    opt_dirs = ['prep_m', 'prep_a', 'reg_m', 'reg_a', 'nuis_a']
    clean_dirs = ['nuis_m']
    label_dirs = ['ts_roi', 'conn']  # create label level granularity

    namer.add_dirs(paths, labels, label_dirs)
    qc_stats = "{}/{}_stats.csv".format(namer.dirs['qa']['base'],
        namer.get_mod_source())

    # Create derivative output file names
    reg_fname = "{}_{}".format(namer.get_mod_source(),
        namer.get_template_info())
    reg_aname = "{}_{}".format(namer.get_anat_source(),
        namer.get_template_info())
    
    preproc_func = namer.name_derivative(namer.dirs['output']['prep_m'],
        "{}_preproc.nii.gz".format(namer.get_mod_source()))
    motion_func = namer.name_derivative(namer.dirs['tmp']['prep_m'],
        "{}_variant-mc_preproc.nii.gz".format(namer.get_mod_source()))
    preproc_t1w_brain = namer.name_derivative(namer.dirs['output']['prep_a'],
        "{}_preproc_brain.nii.gz".format(namer.get_anat_source()))

    aligned_func = namer.name_derivative(namer.dirs['output']['reg_m'],
        "{}_registered.nii.gz".format(reg_fname))
    aligned_t1w = namer.name_derivative(namer.dirs['output']['reg_a'],
        "{}_registered.nii.gz".format(reg_aname))
    
    nuis_func = namer.name_derivative(namer.dirs['output']['nuis_f'],
        "{}_clean.nii.gz".format(reg_fname))
    voxel_ts = namer.name_derivative(namer.dirs['output']['ts_voxel'],
        "{}_timeseries.nii.gz".format(reg_fname))

    print("This pipeline will produce the following derivatives...")
    if not clean:
        print("fMRI volumes preprocessed: {}".format(preproc_func))
        print("T1w volume preprocessed: {}".format(preproc_t1w_brain))
        print("fMRI volume registered to template: {}".format(aligned_func))
        print("T1w volume registered to template: {}".format(aligned_func))
        print("fMRI volumes preprocessed: {}".format(preproc_func))
    print("fMRI Cleaned of Nuisance Variables: {}".format(nuis_func))

    if big:
        print("Voxel timecourse in template space: {}".format(voxel_ts))

    # Again, connectomes are different
    if not isinstance(labels, list):
        labels = [labels]
    connectomes = [namer.name_derivative(
        namer.dirs['output']['conn'][namer.get_label(lab)],
        "{}_{}_measure-correlation.{}".format(namer.get_mod_source(),
            namer.get_label(lab), fmt)) for lab in labels]

    roi_ts = [namer.name_derivative(
        namer.dirs['output']['ts_roi'][namer.get_label(lab)],
        "{}_{}_variant-mean_timeseries.npz".format(namer.get_mod_source(),
                                                   namer.get_label(lab)))
        for lab in labels]

    print("ROI timeseries downsampled to given labels: " +
          ", ".join(roi_ts))
    print("Connectomes downsampled to given labels: " +
          ", ".join(connectomes))

    qc_func = qa_mri(namer, 'func')  # for quality control
    # Align fMRI volumes to Atlas
    # -------- Preprocessing Steps --------------------------------- #
    print "Preprocessing volumes..."
    f_prep = mgfp(func, preproc_func, motion_func, namer.dirs['tmp']['prep_m'])
    f_prep.preprocess(stc=stc)
    try:
        qc_func.func_preproc_qa(f_prep)
    except Exception as e:
        print("Exception in Preprocessing QA.")
    a_prep = mgap(t1w, preproc_t1w_brain, namer.dirs['tmp']['prep_a'])
    a_prep.preprocess()
    try:
        qc_func.anat_preproc_qa(a_prep)
    except Exception as e:
        print("Exception in Preprocessing QA.")

    # ------- Alignment Steps -------------------------------------- #
    print "Aligning volumes..."
    func_reg = mgreg(preproc_func, t1w, preproc_t1w_brain,
                     atlas, atlas_brain, atlas_mask, aligned_func,
                     aligned_t1w, namer)
    func_reg.self_align()
    try:
        qc_func.self_reg_qa(func_reg)
    except Exception as e:
        print("Exception in Self Registration QA.")
    func_reg.template_align()
    try:
        qc_func.temp_reg_qa(func_reg)
    except Exception as e:
        print("Exception in Template Registration QA.")

    # ------- Nuisance Correction Steps ---------------------------- #
    print "Correcting Nuisance Variables..."
    nuis = mgn(aligned_func, aligned_t1w, nuis_func, namer.dirs['tmp'],
               lv_mask=lv_mask, mc_params=f_prep.mc_params)
    nuis.nuis_correct()
    try:
        qc_func.nuisance_qa(nuis)
    except Exception as e:
        print("Exception in Nuisance Correction QA.")

    # ------ Voxelwise Timeseries Steps ---------------------------- #
    if big:
        print "Extracting Voxelwise Timeseries..."
        voxel = mgts().voxel_timeseries(nuis_func, atlas_mask, voxel_ts)
        try:
            qc_func.voxel_ts_qa(voxel, nuis_func, atlas_mask)
        except Exception as e:
            print("Exception in Voxel Timeseries QA.")

    # ------ ROI Timeseries Steps ---------------------------------- #
    for idx, label in enumerate(labels):
        print("Extracting ROI timeseries for {} parcellation...".format(label))
        ts = mgts().roi_timeseries(nuis_func, labels[idx], roi_ts[idx])
        connectome = mgg(ts.shape[0], labels[idx], sens="func")
        conn = connectome.cor_graph(ts)
        connectome.save_graph(connectomes[idx])
        try:
            qc_func.roi_graph_qa(ts, conn, aligned_func,
                                 aligned_t1w, labels[idx])
        except Exception as e:
            erm = "Exception in Connectome Extraction for {} parcellation."
            print(erm.format(labels[idx]))

    # save our statistics so that we can do group level
    exe_time = datetime.now() - startTime
    qc_func.save(qc_stats, exe_time)

    # Clean temp files
    if clean:
        print("Cleaning up intermediate files... ")
        del_dirs = [namer.dirs['tmp']['base']] + \
            [namer.dirs['output'][k] for k in opt_dirs]
        cmd = "rm -rf {}".format(" ".format(del_dirs))
        mgu.execute_cmd(cmd)

    print("Execution took: {}".format(exe_time))
    print("Complete!")
    sys.exit(0)


def ndmg_func_pipeline(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                       labels, outdir, clean=False, stc=None,
                       big=False):
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
    """
    try:
        ndmg_func_worker(func, t1w, atlas, atlas_brain, atlas_mask, lv_mask,
                         labels, outdir, clean=clean, stc=stc,
                         big=big)
    except Exception, e:
        print(traceback.format_exc())
        os.exit() 
    finally:
        try:
            os.exit()
        except Exception, e:
            os.exit()
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
    parser.add_argument("-b", "--big", action="store_true", default=False,
                        help="Whether to produce voxelwise timeseries.")
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
                       result.clean, result.stc, result.big)

if __name__ == "__main__":
    main()
