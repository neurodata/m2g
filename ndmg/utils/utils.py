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
        """

        # Load Data
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

        print(gtab.info)
        return gtab

    def load_bval_bvec(self, fbval, fbvec):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**
        """

        bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

        gtab = gradient_table(bvals, bvecs, atol=0.01)

        print(gtab.info)
        return gtab

    def get_b0(self, gtab, data):
        """
        Takes bval and bvec files and produces a structure in dipy format

        **Positional Arguments:**
        """

        b0 = np.where(gtab.b0s_mask)[0]
        b0_vol = np.squeeze(data[:, :, :, b0[0]])  # if more than 1, use first
        return b0_vol

    def get_filename(self, label):
        """
        Given a fully qualified path gets just the file name, without extension
        """
        return op.splitext(op.splitext(op.basename(label))[0])[0]

    def execute_cmd(self, cmd):
        """
        Given a bash command, it is executed and the response piped back to the
        calling script
        """
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate()
        code = p.returncode
        if code:
            sys.exit("Error  " + str(code) + ": " + err)
        return out, err

    def name_tmps(self, basedir, basename, extension):
        return basedir + "/tmp/" + basename + extension
