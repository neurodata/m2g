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

from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE
import os.path as op
import ndmg.utils as mgu
import ndmg.register as mgr
import ndmg.track as mgt
import ndmg.graph as mgg
import ndmg.preproc as mgp
import numpy as np
import nibabel as nb


def ndmg_pipeline(dti, bvals, bvecs, mprage, atlas, mask, labels, outdir,
                  clean=False, fmt='gpickle'):
    """
    Creates a brain graph from MRI data
    """
    startTime = datetime.now()
    print fmt

    # Create derivative output directories
    dti_name = op.splitext(op.splitext(op.basename(dti))[0])[0]
    cmd = "mkdir -p " + outdir + "/reg_dti " + outdir + "/tensors " +\
          outdir + "/fibers " + outdir + "/graphs"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()

    # Graphs are different because of multiple atlases
    if isinstance(labels, list):
        label_name = [op.splitext(op.splitext(op.basename(x))[0])[0]
                      for x in labels]
        for label in label_name:
            p = Popen("mkdir -p " + outdir + "/graphs/" + label,
                      stdout=PIPE, stderr=PIPE, shell=True)
    else:
        label_name = op.splitext(op.splitext(op.basename(labels))[0])[0]
        p = Popen("mkdir -p " + outdir + "/graphs/" + label_name,
                  stdout=PIPE, stderr=PIPE, shell=True)
    # Create derivative output file names
    aligned_dti = outdir + "/reg_dti/" + dti_name + "_aligned.nii.gz"
    tensors = outdir + "/tensors/" + dti_name + "_tensors.npz"
    fibers = outdir + "/fibers/" + dti_name + "_fibers.npz"
    print "This pipeline will produce the following derivatives..."
    print "DTI volume registered to atlas: " + aligned_dti
    print "Diffusion tensors in atlas space: " + tensors
    print "Fiber streamlines in atlas space: " + fibers

    # Again, graphs are different
    graphs = [outdir + "/graphs/" + x + '/' + dti_name + "_" + x + '.' + fmt
              for x in label_name]
    print "Graphs of streamlines downsampled to given labels: " +\
          (", ".join([x for x in graphs]))

    # Creates gradient table from bvalues and bvectors
    print "Generating gradient table..."
    dti1 = outdir + "/tmp/" + dti_name + "_t1.nii.gz"
    bvecs1 = outdir + "/tmp/" + dti_name + "_1.bvec"
    mgp.rescale_bvec(bvecs, bvecs1)
    gtab = mgu().load_bval_bvec_dti(bvals, bvecs1, dti, dti1)

    # Align DTI volumes to Atlas
    print "Aligning volumes..."
    mgr().dti2atlas(dti1, gtab, mprage, atlas, aligned_dti, outdir)

    print "Beginning tractography..."
    # Compute tensors and track fiber streamlines
    tens, tracks = mgt().eudx_basic(aligned_dti, mask, gtab, stop_val=0.2)

    # And save them to disk
    np.savez(tensors, tens)
    np.savez(fibers, tracks)

    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(label_name):
        print "Generating graph for " + label + " parcellation..."
        labels_im = nb.load(labels[idx])
        g1 = mgg(len(np.unique(labels_im.get_data()))-1, labels[idx])
        g1.make_graph(tracks)
        g1.summary()
        g1.save_graph(graphs[idx], fmt=fmt)

    print "Execution took: " + str(datetime.now() - startTime)

    # Clean temp files
    if clean:
        print "Cleaning up intermediate files... "
        cmd = 'rm -f ' + tensors + ' ' + dti1 + ' ' + aligned_dti + ' ' +\
              bvecs1
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()

    print "Complete!"
    pass


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("dti", action="store", help="Nifti DTI image stack")
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
    parser.add_argument("-f", "--fmt", action="store", default='gpickle',
                        help="Determines graph output format")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p " + result.outdir + " " + result.outdir + "/tmp"
    print "Creating output directory: " + result.outdir
    print "Creating output temp directory: " + result.outdir + "/tmp"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()

    ndmg_pipeline(result.dti, result.bval, result.bvec, result.mprage,
                  result.atlas, result.mask, result.labels, result.outdir,
                  result.clean, result.fmt)


if __name__ == "__main__":
    main()
