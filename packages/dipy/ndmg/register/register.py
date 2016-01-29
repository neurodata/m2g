#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

# register.py
# Created by Greg Kiar on 2016-01-28.
# Email: gkiar@jhu.edu

import os.path as op
from subprocess import Popen, PIPE
import ndmg.utils as ndu
import nibabel as nb


class register(object):
    def __init__(self):
        pass

    def align(self, inp, ref, xfm):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned
                ref:
                    - Image being aligned to
                xfm:
                    - Returned transform between two images
        """
        cmd = "flirt -in " + inp + " -ref " + ref + " -omat " + xfm +\
              " -cost mutualinfo -bins 256 -dof 12 -searchrx -180 180" +\
              "-searchry -180 180 -searchrz -180 180"
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()
        pass

    def applyxfm(self, inp, ref, xfm, aligned):
        """
        Aligns two images with a given transform

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned
                ref:
                    - Image being aligned to
                xfm:
                    - Transform between two images
                aligned:
                    - Aligned output image
        """
        cmd = "flirt -in " + inp + " -ref " + ref + " -out " + aligned +\
              " -init " + xfm + " -interp trilinear -applyxfm"
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()
        pass

    def dti2atlas(self, dti, gtab, mprage, atlas, aligned_dti):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned
                ref:
                    - Image being aligned to
                xfm:
                    - Returned transform between two images
        """
        # Creates names for all intermediate files used
        b0 = "/tmp/b0.nii.gz"
        xfm1 = "/tmp/tfm1.mat"
        xfm2 = "/tmp/tfm2.mat"
        xfm3 = "/tmp/tfm3.mat"

        # Loads DTI image in as data and extracts B0 volume
        dti_im = nb.load(dti)
        b0_im = ndu.get_b0(gtab, dti_im.get_data())

        # Wraps B0 volume in new nifti image
        b0_head = dti_im.get_header()
        b0_head.set_data_shape(b0_head.get_data_shape()[0:3])
        b0_out = Nifti1Image(b0_im, affine=dti_im.get_affine(), header=b0_head)
        b0_out.update_header()
        nb.save(out, b0)

        # Algins B0 volume to MPRAGE, and MPRAGE to Atlas
        self.align(b0, mprage, xfm1)
        self.align(mprage, atlas, xfm2)

        # Combines transforms from previous registrations in proper order
        cmd = "convert_xfm -omat " + xfm3 + " -concat " + xfm2 + " " + xfm1
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()

        # Applies combined transform to dti image volume
        self.applyxfm(dti, atlas, xfm3, aligned_dti)
        pass
