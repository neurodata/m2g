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

# preproc.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu

import numpy as np
import nibabel as nb
import sys
import os.path as op
import os.path
import nilearn as nl
from ndmg.utils import utils as mgu
from ndmg.qc import qc as mgqc
from scipy import signal


class preproc(object):

    def __init__(self):
        """
        Enables preprocessing of single images for single images. Has options
        to perform motion correction (now).
        """
        pass

    def motion_correct(self, mri, corrected_mri, idx):
        """
        Performs motion correction of a stack of 3D images.

        **Positional Arguments:**
            - mri: the 4d (fMRI) image volume as a nifti file.
            - corrected_mri: the corrected and aligned fMRI image volume.
        """
        cmd = "mcflirt -in " + mri + " -out " + corrected_mri +\
            " -plots -refvol " + str(idx)
        mgu().execute_cmd(cmd)
        pass

    def detrend(self, mri, detrended_mri):
        """
        Removes linear and quadratic trending of a fmri brain.

        *Positional Arguments:*
            mri: the mri to detrend.
            detrended_mri: the mri that is smoothed.
        """
        mri_im = nb.load(mri)
        mri_dat = mgu().get_brain(mri_im)
        dt_mri_dat = signal.detrend(mri_dat)
        mri_mean = np.mean(mri_dat, axis=3)
        nvol = dt_mri_dat.shape[3]
        for t in range(0, nvol):
            dt_mri_dat[:, :, :, t] = dt_mri_dat[:, :, :, t] + mri_mean
        dt_mri = nb.Nifti1Image(dt_mri_dat, mri_im.get_affine())
        nb.save(dt_mri, detrended_mri)
        pass

    def smooth(self, mri, smoothed_mri):
        """
        Smooths a nifti image by applying a fwhm filter of specified diameter.

        *Positional Arguments:*
            mri: the mri to smooth.
            smoothed_mri: the smoothed mri path.
        """
        pass

    def preprocess(self, mri, preproc_mri, motion_mri, outdir, qcdir="",
                   scanid=""):
        """
        A function to preprocess a stack of 3D images.

        **Positional Arguments:**
            - mri: the 4d (fMRI) image volume as a nifti file.
            - preproc_mri: the 4d (fMRI) preprocessed image volume
                as a nifti image.
            - outdir: the location to place outputs
        """

        mri_name = op.splitext(op.splitext(op.basename(mri))[0])[0]

        s0 = outdir + "/tmp/" + mri_name + "_0slice.nii.gz"
        dt_mri = outdir + "/tmp/" + mri_name + "_detrended.nii.gz"

        # TODO EB: decide whether it is advantageous to align to mean image
        self.motion_correct(mri, motion_mri, 0)

        if qcdir is not None:
            mgu().get_slice(motion_mri, 0, s0)
            mgqc().check_alignments(mri, motion_mri, s0, qcdir, mri_name,
                                    title="Motion Correction")
            mgqc().image_align(motion_mri, s0, qcdir, scanid=mri_name,
                               refid=mri_name + "_s0")
            print("Test")

        cmd = "cp " + motion_mri + " " + preproc_mri
        mgu().execute_cmd(cmd)
        # self.detrend(mri, preproc_mri)
        # self.smooth(mri, preproc_mri)
        pass
