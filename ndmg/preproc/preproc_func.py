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

# preproc_func.py
# Created by Eric Bridgeford on 2016-06-20.
# Email: ebridge2@jhu.edu

import numpy as np
import nibabel as nb
import sys
import os.path as op
import os.path
import nilearn as nl
from ndmg import utils as mgu
from scipy import signal


class preproc_func():

    def __init__(self, func, preproc_func, motion_func, outdir):
        """
        Enables preprocessing of single images for single images. Has options
        to perform motion correction.
        """
        self.func = func
        self.preproc_func = preproc_func
        self.motion_func = motion_func
        self.outdir = outdir
        pass

    def motion_correct(self, mri, corrected_mri, idx=None):
        """
        Performs motion correction of a stack of 3D images.

        **Positional Arguments:**
            mri (String):
                 -the 4d (fMRI) image volume as a nifti file.
            corrected_mri (String):
                - the corrected and aligned fMRI image volume.
            idx:
                - the index to use as a reference for self
                  alignment. Uses the meanvolume if not specified
        """
        if idx is None:
            # defaults to mean volume
            cmd = "mcflirt -in {} -out {} -plots -meanvol"
            cmd = cmd.format(mri, corrected_mri)
        else:
            # if user provides a volume index, use it
            cmd = "mcflirt -in {} -out {} -plots -refvol {}"
            cmd = cmd.format(mri, corrected_mri, idx)
        mgu.execute_cmd(cmd, verb=True)

    def slice_time_correct(self, func, corrected_func, tr, stc=None):
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
            elif stc == "up":
                cmd += ''  # default of slicetimer
            elif op.isfile(stc):
                cmd += " --tcustom {}".format(stc)
            cmd += " -r {}".format(tr)
            mgu.execute_cmd(cmd, verb=True)
        else:
            print "Skipping slice timing correction."

    def preprocess(self, stc=None, trim=15):
        """
        A function to preprocess a stack of 3D images.
        """
        func_name = mgu.get_filename(self.func)

        trim_func = "{}/{}_trim.nii.gz".format(self.outdir, func_name)
        stc_func = "{}/{}_stc.nii.gz".format(self.outdir, func_name)

        # trim the first 15 seconds of data while tissue reaches steady state
        # of radiofrequency excitation
        func_im = nb.load(self.func)
        tr = func_im.header.get_zooms()[3]
        if tr == 0:
            raise ZeroDivisionError('Failed to determine number of frames to'
                                    ' trim due to tr=0.')
        nvol_trim = int(np.floor(15/float(tr)))
        # remove the first nvol_trim timesteps
        mssg = ("Scrubbing first 15 seconds ({0:d} volumes due"
                " to tr={1: .3f}s)")
        print(mssg.format(nvol_trim, tr))
        trimmed_dat = func_im.get_data()[:,:,:, nvol_trim:]
        trimmed_im = nb.Nifti1Image(dataobj=trimmed_dat,
                                    header=func_im.header,
                                    affine=func_im.affine)
        nb.save(img=trimmed_im, filename=trim_func)


        # use slicetimer if user passes slicetiming information
        if (stc is not None):
            self.slice_time_correct(trim_func, stc_func, tr, stc)
        else:
            stc_func = trim_func
        # motion correct using the mean volume (FSL default)
        self.motion_correct(stc_func, self.motion_func, None)
        self.mc_params = "{}.par".format(self.motion_func)
        cmd = "cp {} {}".format(self.motion_func, self.preproc_func)
        mgu.execute_cmd(cmd, verb=True)
