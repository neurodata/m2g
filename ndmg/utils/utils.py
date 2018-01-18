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

# utils.py
# Created by Will Gray Roncal on 2016-01-28.
# Email: wgr@jhu.edu

from __future__ import print_function

from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from subprocess import Popen, PIPE
import numpy as np
import nibabel as nb
import os.path as op
import sys


def apply_mask(inp, masked, mask):
    """
    A function to apply a mask to a brain.

    **Positional Arguments:**
        inp:
            - the input path to an mri image.
        masked:
            - the output path to the masked image.
        mask:
            - the path to a brain mask.
    """
    cmd = "fslmaths {} -mas {} {}".format(inp, mask, masked)
    execute_cmd(cmd)
    pass


def load_bval_bvec_dwi(fbval, fbvec, dwi_file, dwi_file_out):
    """
    Takes bval and bvec files and produces a structure in dipy format

    **Positional Arguments:**
    """

    # Load Data
    img = nb.load(dwi_file)
    data = img.get_data()

    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

    # Get rid of spurrious scans
    idx = np.where((bvecs[:, 0] == 100) & (bvecs[:, 1] == 100) &
                   (bvecs[:, 2] == 100))
    bvecs = np.delete(bvecs, idx, axis=0)
    bvals = np.delete(bvals, idx, axis=0)
    data = np.delete(data, idx, axis=3)

    # Save corrected DTI volume
    dwi_new = nb.Nifti1Image(data, affine=img.get_affine(),
                             header=img.get_header())
    dwi_new.update_header()
    nb.save(dwi_new, dwi_file_out)

    gtab = gradient_table(bvals, bvecs, atol=0.01)

    print(gtab.info)
    return gtab


def load_bval_bvec(fbval, fbvec):
    """
    Takes bval and bvec files and produces a structure in dipy format

    **Positional Arguments:**
    """

    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    gtab = gradient_table(bvals, bvecs, atol=0.01)

    print(gtab.info)
    return gtab


def get_b0(gtab, data):
    """
    Takes bval and bvec files and produces a structure in dipy format

    **Positional Arguments:**
    """

    b0 = np.where(gtab.b0s_mask)[0]
    b0_vol = np.squeeze(data[:, :, :, b0[0]])  # if more than 1, use first
    return b0_vol


def get_filename(label):
    """
    Given a fully qualified path gets just the file name, without extension
    """
    return op.splitext(op.splitext(op.basename(label))[0])[0]


def get_slice(mri, volid, sli):
    """
    Takes a volume index and constructs a new nifti image from
    the specified volume.
    **Positional Arguments:**
        mri:
            - the path to a 4d mri volume to extract a slice from.
        volid:
            - the index of the volume desired.
        sli:
            - the path to the destination for the slice.
    """
    mri_im = nb.load(mri)
    data = mri_im.get_data()
    # get the slice at the desired volume
    vol = np.squeeze(data[:, :, :, volid])

    # Wraps volume in new nifti image
    head = mri_im.get_header()
    head.set_data_shape(head.get_data_shape()[0:3])
    out = nb.Nifti1Image(vol, affine=mri_im.get_affine(),
                         header=head)
    out.update_header()
    # and saved to a new file
    nb.save(out, sli)


def get_braindata(brain_file):
    """
    Opens a brain data series for a mask, mri image, or atlas.
    Returns a numpy.ndarray representation of a brain.

    **Positional Arguements**
        brain_file:
            - an object to open the data for a brain.
            Can be a string (path to a brain file),
            nibabel.nifti1.nifti1image, or a numpy.ndarray
    """
    if type(brain_file) is np.ndarray:  # if brain passed as matrix
        braindata = brain_file
    else:
        if type(brain_file) is str or type(brain_file) is unicode:
            brain = nb.load(str(brain_file))
        elif type(brain_file) is nb.nifti1.Nifti1Image:
            brain = brain_file
        else:
            raise TypeError("Brain file is type: {}".format(type(brain_file)) +
                            "; accepted types are numpy.ndarray, "
                            "string, and nibabel.nifti1.Nifti1Image.")
        braindata = brain.get_data()
    return braindata


def extract_brain(inp, out, opts=""):
    """
    A function to extract the brain from an image using FSL's BET.

    **Positional Arguments:**
        inp:
            - the input image.
        out:
            - the output brain extracted image.
    """
    cmd = "bet {} {} {}".format(inp, out, opts)
    execute_cmd(cmd)


def execute_cmd(cmd, verb=False):
    """
    Given a bash command, it is executed and the response piped back to the
    calling script
    """
    if verb:
        print("Executing: {}".format(cmd))

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    code = p.returncode
    if code:
        sys.exit("Error {}: {}".format(code, err))
    return out, err


def name_tmps(basedir, basename, extension):
    return "{}/tmp/{}{}".format(basedir, basename, extension)

