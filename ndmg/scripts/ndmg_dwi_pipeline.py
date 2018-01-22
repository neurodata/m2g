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

# ndmg_pipeline.py
# Created by Greg Kiar and Will Gray Roncal on 2016-01-27.
# Email: gkiar@jhu.edu, wgr@jhu.edu

from __future__ import print_function

from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE
from ndmg.stats.qa_reg import *
from ndmg.stats.qa_tensor import *
from ndmg.stats.qa_fibers import *
import ndmg.utils as mgu
import ndmg.register as mgr
import ndmg.track as mgt
import ndmg.graph as mgg
import ndmg.preproc as mgp
import numpy as np
import nibabel as nb
import os


def ndmg_dwi_pipeline(dwi, bvals, bvecs, mprage, atlas, mask, labels, outdir,
                  clean=False, fmt='edgelist'):
    """
    Creates a brain graph from MRI data
    """
    startTime = datetime.now()

    # Create derivative output directories
    dwi_name = mgu.get_filename(dwi)
    cmd = "mkdir -p {}/reg/dwi {}/tensors {}/fibers {}/graphs \
           {}/qa/tensors {}/qa/tensors {}/qa/fibers {}/qa/reg/dwi"
    cmd = cmd.format(*([outdir] * 8))
    mgu.execute_cmd(cmd)

    # Graphs are different because of multiple parcellations
    if isinstance(labels, list):
        label_name = [mgu.get_filename(x) for x in labels]
        for label in label_name:
            mgu.execute_cmd("mkdir -p {}/graphs/{}".format(outdir, label))
    else:
        label_name = mgu.get_filename(labels)
        mgu.execute_cmd("mkdir -p {}/graphs/".format(outdir, label_name))

    # Create derivative output file names
    aligned_dwi = "{}/reg/dwi/{}_aligned.nii.gz".format(outdir, dwi_name)
    tensors = "{}/tensors/{}_tensors.npz".format(outdir, dwi_name)
    fibers = "{}/fibers/{}_fibers.npz".format(outdir, dwi_name)
    print("This pipeline will produce the following derivatives...")
    print("DWI volume registered to atlas: {}".format(aligned_dwi))
    print("Diffusion tensors in atlas space: {}".format(tensors))
    print("Fiber streamlines in atlas space: {}".format(fibers))

    # Again, graphs are different
    graphs = ["{}/graphs/{}/{}_{}.{}".format(outdir, x, dwi_name, x, fmt)
              for x in label_name]
    print("Graphs of streamlines downsampled to given labels: " +
          ", ".join([x for x in graphs]))

    # Creates gradient table from bvalues and bvectors
    print("Generating gradient table...")
    dwi1 = "{}/tmp/{}_t1.nii.gz".format(outdir, dwi_name)
    bvecs1 = "{}/tmp/{}_1.bvec".format(outdir, dwi_name)
    mgp.rescale_bvec(bvecs, bvecs1)
    gtab = mgu.load_bval_bvec_dwi(bvals, bvecs1, dwi, dwi1)

    # Align DWI volumes to Atlas
    print("Aligning volumes...")
    mgr().dwi2atlas(dwi1, gtab, mprage, atlas, aligned_dwi, outdir, clean)
    loc0 = np.where(gtab.b0s_mask)[0][0]
    reg_mri_pngs(aligned_dwi, atlas, "{}/qa/reg/dwi/".format(outdir), loc=loc0)

    print("Beginning tractography...")
    # Compute tensors and track fiber streamlines
    tens, tracks = mgt().eudx_basic(aligned_dwi, mask, gtab, stop_val=0.2)
    tensor2fa(tens, tensors, aligned_dwi, "{}/tensors/".format(outdir),
              "{}/qa/tensors/".format(outdir))

    # As we've only tested VTK plotting on MNI152 aligned data...
    if nb.load(mask).get_data().shape == (182, 218, 182):
        try:
            visualize_fibs(tracks, fibers, mask,
                           "{}/qa/fibers/".format(outdir), 0.02)
        except:
            print("Fiber QA failed - VTK for Python not configured properly.")

    # And save them to disk
    np.savez(tensors, tens)
    np.savez(fibers, tracks)

    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(label_name):
        print("Generating graph for {} parcellation...".format(label))

        labels_im = nb.load(labels[idx])
        g1 = mgg(len(np.unique(labels_im.get_data()))-1, labels[idx])
        g1.make_graph(tracks)
        g1.summary()
        g1.save_graph(graphs[idx], fmt=fmt)

    print("Execution took: {}".format(datetime.now() - startTime))

    # Clean temp files
    if clean:
        print("Cleaning up intermediate files... ")
        cmd = 'rm -f {} tmp/{}* {} {}'.format(tensors, dwi_name,
                                               aligned_dwi, fibers)
        mgu.execute_cmd(cmd)

    print("Complete!")


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("dwi", action="store", help="Nifti DTI image stack")
    parser.add_argument("bval", action="store", help="DTI scanner b-values")
    parser.add_argument("bvec", action="store", help="DTI scanner b-vectors")
    parser.add_argument("mprage", action="store", help="Nifti T1 MRI image")
    parser.add_argument("atlas", action="store", help="Nifti T1 MRI atlas")
    parser.add_argument("mask", action="store", help="Nifti binary mask of \
                        brain space in the atlas")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    parser.add_argument("-c", "--clean", action="store_true", default=False,
                        help="Whether or not to delete intemediates")
    parser.add_argument("-f", "--fmt", default='edgelist',
                        choices=['gpickle', 'graphml', 'edgelist'],
                        help="Determines graph output format")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p {} {}/tmp".format(result.outdir, result.outdir)
    print("Creating output directory: {}".format(result.outdir))
    print("Creating output temp directory: {}/tmp".format(result.outdir))
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()

    ndmg_dwi_pipeline(result.dwi, result.bval, result.bvec, result.mprage,
                      result.atlas, result.mask, result.labels, result.outdir,
                      result.clean, result.fmt)


if __name__ == "__main__":
    main()
