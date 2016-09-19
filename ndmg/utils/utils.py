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

from itertools import combinations
from datetime import datetime
from dipy.io import read_bvals_bvecs, read_bvec_file
from dipy.core.gradients import gradient_table
from subprocess import Popen, PIPE
import numpy as np
import nibabel as nb
import os.path as op
import sys


class utils():
    def __init__(self):
        """
        Utility functions for m2g
        """

        pass

    def load_bval_bvec_dti(self, fbval, fbvec, dti_file, dti_file_out):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**

                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """

        # Load Data
        startTime = datetime.now()

        img = nb.load(dti_file)
        data = img.get_data()

        bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

        # Get rid of spurrious scans
        idx = np.where((bvecs[:, 0] == 100) & (bvecs[:, 1] == 100) &
                       (bvecs[:, 2] == 100))
        bvecs = np.delete(bvecs, idx, axis=0)
        bvals = np.delete(bvals, idx, axis=0)
        data = np.delete(data, idx, axis=3)

        # Save corrected DTI volume
        dti_new = nb.Nifti1Image(data, affine=img.get_affine(),
                                 header=img.get_header())
        dti_new.update_header()
        nb.save(dti_new, dti_file_out)

        gtab = gradient_table(bvals, bvecs, atol=0.01)

        print gtab.info
        return gtab

    def load_bval_bvec(self, fbval, fbvec):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**

                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """

        bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

        gtab = gradient_table(bvals, bvecs, atol=0.01)

        print gtab.info
        return gtab

    def get_b0(self, gtab, data):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**

                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """

        b0 = np.where(gtab.b0s_mask)[0]
        b0_vol = np.squeeze(data[:, :, :, b0])  # if more than 1, use first one
        return b0_vol

    def get_filename(self, label):
        """
        Given a fully qualified path gets just the file name, without extension
        """
        return op.splitext(op.splitext(op.basename(label))[0])[0]

    def get_slice(self, mri, volid, sli):
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
        pass

    def get_brain(self, brain_file):
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
                raise TypeError("Mask file is of type " + str(type(brain_file)) +
                                "; accepted types are numpy.ndarray, " +
                                "string, and nibabel.nifti1.Nifti1Image.")
            braindata = brain.get_data()
        return braindata

    def apply_mask(self, inp, masked, mask):
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
        cmd = "fslmaths " + inp + " -mas " + mask + " " + masked
        self.execute_cmd(cmd)
        pass

    def extract_brain(self, inp, out, opts=""):
        """
        A function to extract the brain from an image using FSL's BET.

        **Positional Arguments:**
            inp:
                - the input image.
            out:
                - the output brain extracted image.
        """
        cmd = "bet " + inp + " " + out
        if opts is not None:
            cmd = cmd + " " + str(opts)
        self.execute_cmd(cmd)
        pass

    def execute_cmd(self, cmd):
        """
        Given a bash command, it is executed and the response piped back to the
        calling script

        **Positional Arguments:**
            cmd:
                - the bash command to execute.
        """
        print("Executing: " + cmd)
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        code = p.returncode
        if code:
            sys.exit("Error  " + str(code) + ": " + err)
        return out, err

    def get_b0(self, gtab, data):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**
                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """

        b0 = np.where(gtab.b0s_mask)[0]
        b0_vol = np.squeeze(data[:, :, :, b0])  # if more than 1, use first one
        return b0_vol

    def name_tmps(self, basedir, basename, extension):
        return basedir + "/tmp/" + basename + extension
