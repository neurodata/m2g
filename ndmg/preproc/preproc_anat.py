#!/usr/bin/env python

# Copyright 2017 NeuroData (http://neurodata.io)
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

# preproc_anat.py
# Created by Eric Bridgeford on 2017-06-20.
# Email: ebridge2@jhu.edu

import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgru
import nibabel as nb


class preproc_anat:
    def __init__(self, anat, anat_preproc_brain, outdir):
        """
        Enables preprocessing of anatomical images, using AFNI.

        **Positional Arguments:**

            - anat:
                - the raw anatomical image.
            - anat_preproc:
                - the preprocessed anatomical image.
            - anat_preproc_brain:
                - the preprocessed anatomical brain image.
            - outdir:
                - the output directory.
        """
        self.anat = anat
        self.anat_name = mgu.get_filename(anat)
        self.anat_preproc_brain = anat_preproc_brain
        self.outdir = outdir

    def preprocess(self):
        """
        A function to to perform anatomical preprocessing.

        **Positional Argument:**

            - res:
                - the resampling resolution to use if the input is high res.
        """
        mgru.extract_t1w_brain(self.anat, self.anat_preproc_brain, self.outdir)
        pass
