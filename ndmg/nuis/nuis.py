#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neuromri_dat.io)
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

# nuis.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu
from ndmg.utils import utils as mgu
# from CPAC.nuisance import calc_compcor_components
import nibabel as nb
import numpy as np


class nuis(object):

    def __init__(self):
        """
        A class for nuisance correction of fMRI.
        """
        pass

    def highpass_filter(self, mri, bandpass_mri):
        """
        A function that uses FSL's fslmaths to high pass
        an fMRI image.

        **Positional Arguments:**
            mri:
                - the unfiltered image.
            bandpass_mri:
                - the image with low frequency signal removed.
        """
        mri_im = nb.load(mri)
        highpass = 1/.01 # above this freq we want to include
        low = -1 # below this freq we want to include, -1
                 # includes all (ignore low pass)
        tr = mri_im.header.get_zooms()[3]
        sigma_high = highpass/(2*tr)

        cmd = "fslmaths " + mri + " -bptf " + str(sigma_high) + " " +\
            str(low) + " " + bandpass_mri
        mgu().execute_cmd(cmd)

    def nuis_correct(self, mri, nuisance_mri):
        """
        A function for nuisance correction on an aligned fMRI
        image. So far, this only highpass filters.

        **Positional Arguments:**
            mri:
                - the mri file.
            nuisance_mri:
                - the nuisance corrected filename.
        """
        self.highpass_filter(mri, nuisance_mri)
        pass
