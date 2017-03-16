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

# preproc_fmri.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu

import numpy as np
import nibabel as nb
import sys
import os.path as op
import os.path
import nilearn as nl
from ndmg.utils import utils as mgu
from scipy import signal
from ndmg.stats import qa_reg_func as mgrq


class preproc_func():

    def __init__(self):
        """
        Enables preprocessing of single images for single images. Has options
        to perform motion correction.
        """
        pass

    def motion_correct(self, mri, corrected_mri, idx):
        """
        Performs motion correction of a stack of 3D images.

        **Positional Arguments:**
            mri (String):
                 -the 4d (fMRI) image volume as a nifti file.
            corrected_mri (String):
                - the corrected and aligned fMRI image volume.
        """
        cmd = "mcflirt -in {} -out {} -plots -refvol {}"
        cmd = cmd.format(mri, corrected_mri, idx)
        mgu.execute_cmd(cmd)

    def slice_time_correct(self, func, corrected_func, stc=None):
        """
        Performs slice timing correction of a stack of 3D images.

        **Positional Arguments:**
            mri (String):
                 -the 4d (fMRI) image volume as a nifti file.
            corrected_mri (String):
                - the corrected and aligned fMRI image volume.
            stc: the slice timing correction options, a string
                  corresponding to the acquisition sequence.
                  Options are "/path/to/file", "down", "up",
                  "interleaved". If a file is passed, each line
                  should correspond to a single value (in TRs)
                  of the shift of each slice. For example,
                  if the first slice has no shift, the first line
                  in the text file would be "0.5".
                  If not None, make sure the "zooms" property is set
                  in your data (nb.load(mri).header.get_zooms()), otherwise
                  this function will throw an error.
        """
        if (stc is not None):
            cmd = "slicetimer -i {} -o {}".format(func, corrected_func)
            if stc == "down":
                cmd += " --down"
            elif stc == "interleaved":
                cmd += " --odd"
            elif op.isfile(stc):
                cmd += " --tcustom {}".format(stc)
            zooms = nb.load(func).header.get_zooms()
            cmd += " -r {}".format(zooms[3])
            mgu.execute_cmd(cmd)
        else:
            print "Skipping slice timing correction."

    def preprocess(self, func, preproc_func, motion_func,
                   outdir, stc=None, qcdir="", scanid=""):
        """
        A function to preprocess a stack of 3D images.

        **Positional Arguments:**

            mri:
                - the 4d (fMRI) image volume as a nifti file (String).
            motion_mri:
                - the 4d (fMRI) image volume that is motion aligned (String).
            preproc_mri:
                - the 4d (fMRI) preprocessed image volume
                as a nifti image (String).
            stc:
                - the slice timing correction information. See documentation
                  for slice_time_correct() for details.
            mri_name:
                - the name to append before all paths for file naming.
            outdir:
                - the location to place outputs (String).
            qcdir:
                - optional argument required for quality control output
                directory (String).
            scanid:
                - optional argument required for quality control, is the id
                of the subject (String).
        """
        func_name = mgu.get_filename(func)

        s0 = mgu.name_tmps(outdir, func_name, "_0slice.nii.gz")
        stc_func = mgu.name_tmps(outdir, func_name, "_stc.nii.gz")
        # TODO EB: decide whether it is advantageous to align to mean image
        if (stc is not None):
            self.slice_time_correct(func, stc_func, stc)
        else:
            stc_func = func
        self.motion_correct(stc_func, motion_func, 0)

        cmd = "cp {} {}".format(motion_func, preproc_func)
        mgu.execute_cmd(cmd)
