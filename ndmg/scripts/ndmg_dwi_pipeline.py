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

# ndmg_dwi_pipeline.py
# Created by Greg Kiar and Will Gray Roncal on 2016-01-27.
# Email: gkiar@jhu.edu, wgr@jhu.edu
# Edited by Eric Bridgeford on 2017-07-13.

from __future__ import print_function
from datetime import datetime
import time
from ndmg.stats.qa_tensor import *
from ndmg.stats.qa_fibers import *
from ndmg.stats.qa_mri import qa_mri
import ndmg.utils as mgu
import ndmg.register as mgr
import ndmg.track as mgt
import ndmg.graph as mgg
import ndmg.preproc as mgp
import numpy as np
import nibabel as nib
import os
from ndmg.graph import biggraph as ndbg
import traceback
from ndmg.utils.bids_utils import name_resource
import sys


os.environ["MPLCONFIGDIR"] = "/tmp/"


def ndmg_dwi_worker(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                    clean=False, big=False):
    """
    Creates a brain graph from MRI data
    """
    startTime = datetime.now()
    fmt = '_elist.csv'
    # Create derivative output directories
    namer = name_resource(dwi, t1w, atlas, outdir)

    paths = {'prep_m': "dwi/preproc",
             'prep_a': "anat/preproc",
             'reg_m': "dwi/registered",
             'reg_a': "anat/registered",
             'tensor': "dwi/tensor",
             'fiber': "dwi/fiber",
             'voxelg': "dwi/voxel-connectomes",
             'conn': "dwi/roi-connectomes"}

    opt_dirs = ['prep_m', 'prep_a', 'reg_m', 'reg_a']
    clean_dirs = ['tensor', 'fiber']
    label_dirs = ['conn']  # create label level granularity

    namer.add_dirs(paths, labels, label_dirs)
    qc_stats = "{}/{}_stats.csv".format(namer.dirs['qa']['base'],
        namer.get_mod_source())

    # Create derivative output file names
    reg_dname = "{}_{}".format(namer.get_mod_source(),
        namer.get_template_info())
    reg_aname = "{}_{}".format(namer.get_anat_source(),
        namer.get_template_info())
    `
    preproc_dwi = namer.name_derivative(namer.dirs['output']['prep_m'],
        "{}_preproc.nii.gz".format(namer.get_mod_source()))
    motion_dwi = namer.name_derivative(namer.dirs['tmp']['prep_m'],
        "{}_variant-mc_preproc.nii.gz".format(namer.get_mod_source()))
    preproc_t1w_brain = namer.name_derivative(namer.dirs['output']['prep_a'],
        "{}_preproc_brain.nii.gz".format(namer.get_anat_source()))

    aligned_dwi = namer.name_derivative(namer.dirs['output']['reg_m'],
        "{}_registered.nii.gz".format(reg_dname))
    aligned_t1w = namer.name_derivative(namer.dirs['output']['reg_a'],
        "{}_registered.nii.gz".format(reg_aname))

    tensors = namer.name_derivative(namer.dirs['output']['tensor'],
        "{}_tensor.npz".format(reg_dname))
    fibers = namer.name_derivative(namer.dirs['output']['fiber'],
        "{}_fibers.npz".format(reg_dname))

    print("This pipeline will produce the following derivatives...")
    if not clean:
        print("dMRI volumes preprocessed: {}".format(preproc_dwi))
        print("T1w volume preprocessed: {}".format(preproc_t1w_brain))
        print("dMRI volume registered to template: {}".format(aligned_dwi))
    print("dMRI Tensors: {}".format(tensors))
    print("dMRI Fibers: {}".format(fibers))

    if big:
        voxel = namer.name_derivative(namer.dirs['output']['voxel'],
            "{}_voxel-connectome.npz".format(reg_dname))
        print("Voxelwise Fiber Graph: {}".format(voxel))

    # Again, connectomes are different
    if not isinstance(labels, list):
        labels = [labels]
    connectomes = [namer.name_derivative(
        namer.dirs['output']['conn'][namer.get_label(lab)],
        "{}_{}_measure-spatial-ds.{}".format(namer.get_mod_source(),
            namer.get_label(lab), fmt)) for lab in labels]

    print("Connectomes downsampled to given labels: " +
          ", ".join(connectomes))

    qc_dwi = qa_mri(namer, 'dwi')  # for quality control
    # Align fMRI volumes to Atlas

    # -------- Preprocessing Steps --------------------------------- #
    # Perform eddy correction
    dwi_prep = "{}/eddy_corrected_data.nii.gz".format(outdir['prep'])
    cmd='eddy_correct ' + dwi + ' ' + dwi_prep + ' 0'
    os.system(cmd)

    # Rotate bvecs
    eddy_rot_param = dwi_prep.split('/')[-1].split('.')[0] + 'eddy_corrected_data.ecclog'
    bvec_rotated = bvecs.split('/')[-1].split('.')[0] + 'bvec_rotated'
    cmd='fdt_rotate_bvecs ' + bvecs + ' ' + bvec_rotated + ' ' + eddy_rot_param
    os.system(cmd)

    dwi = dwi_prep
    bvecs = bvec_rotated
    [gtab, nodif_B0_mask] = mgu.make_gtab_and_bmask(bvals, bvecs, dwi, outdir)
    # -------- Registration Steps ----------------------------------- #
    vox_size = '2mm'
    reg = mgr.register(outdir, nodif_B0_mask, t1w, vox_size, simple=False)
    # Perform anatomical segmentation
    start_time = time.time()
    reg.gen_tissue()
    print("%s%s%s" % ('gen_tissue runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # align t1w to dwi
    start_time = time.time()
    reg.t1w2dwi_align()
    print("%s%s%s" % ('t1w2dwi_align runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # align atlas to t1w to dwi
    start_time = time.time()
    for atlas in labels:
        print("%s%s" % ('Applying native-space alignment to ', atlas))
        reg.atlas2t1w2dwi_align(atlas)
    print("%s%s%s" % ('atlas2t1w2dwi_align runtime: ', str(np.round(time.time() - start_time, 1)), 's'))
    # align tissue classifiers
    start_time = time.time()
    reg.tissue2dwi_align()
    print("%s%s%s" % ('tissue2dwi_align runtime: ', str(np.round(time.time() - start_time, 1)), 's'))

    # -------- Tensor Fitting and Fiber Tractography ---------------- #
    # Compute tensors and track fiber streamlines
    print("Beginning tractography...")
    trac = mgt(dwi_prep, reg.nodif_B0_mask, reg.gm_in_dwi, reg.vent_csf_in_dwi,
               reg.wm_in_dwi, reg.wm_in_dwi_bin, gtab,seeds=1000000,
               a_low=0.02, step_sz=0.5, max_points=2000, ang_thr=60.0)

    # As we've only tested VTK plotting on MNI152 aligned data...
    if nib.load(mask).get_data().shape == (182, 218, 182):
        try:
            visualize_fibs(tracks, fibers, mask, namer.dirs['qa']['fiber'], 0.02)
        except:
            print("Fiber QA failed - VTK for Python not configured properly.")

    # And save them to disk
    np.savez(tensors, tens)
    np.savez(fibers, tracks)

    # -------- Big Graph Generation --------------------------------- #
    # Generate big graphs from streamlines
    if big:
        print("Making Voxelwise Graph...")
        bg1 = ndbg()
        bg1.make_graph(tracks)
        bg1.save_graph(voxel)

    # ------- Connectome Estimation --------------------------------- #
    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(labels):
        print("Generating graph for {} parcellation...".format(label))

        labels_im = nib.load(labels[idx])
        g1 = mgg(len(np.unique(labels_im.get_data()))-1, labels[idx])
        g1.make_graph(tracks)
        g1.summary()
        g1.save_graph(connectomes[idx])

    exe_time = datetime.now() - startTime
    qc_dwi.save(qc_stats, exe_time)

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


def ndmg_dwi_pipeline(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                      clean=False, big=False):
    """
    A wrapper for the worker to make our pipeline more robust to errors.
    """
    try:
        ndmg_dwi_worker(dwi, bvals, bvecs, t1w, atlas, mask, labels, outdir,
                        clean, big)
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
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("dwi", action="store", help="Nifti DTI image stack")
    parser.add_argument("bval", action="store", help="DTI scanner b-values")
    parser.add_argument("bvec", action="store", help="DTI scanner b-vectors")
    parser.add_argument("t1w", action="store", help="Nifti T1w MRI image")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("mask", action="store", help="Nifti binary mask of \
                        brain space in the atlas")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-b", "--big", action="store_true", default=False,
                        help="whether or not to produce voxelwise big graph")
    result = parser.parse_args()

    # Create output directory
    print("Creating output directory: {}".format(result.outdir))
    print("Creating output temp directory: {}/tmp".format(result.outdir))
    mgu.execute_cmd("mkdir -p {} {}/tmp".format(result.outdir, result.outdir))

    ndmg_dwi_pipeline(result.dwi, result.bval, result.bvec, result.t1w,
                      result.atlas, result.mask, result.labels, result.outdir,
                      result.clean, result.big)


if __name__ == "__main__":
    main()
