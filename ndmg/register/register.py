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
import numpy as np


class register(object):

    def __init__(self):
        """
        Enables registration of single images to one another as well as volumes
        within multi-volume image stacks. Has options to compute transforms,
        apply transforms, as well as a built-in method for aligning low
        resolution dti images to a high resolution atlas.
        """
        pass

    def align(self, inp, ref, xfm):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned as a nifti image file
                ref:
                    - Image being aligned to as a nifti image file
                xfm:
                    - Returned transform between two images
        """
        cmd = "flirt -in " + inp + " -ref " + ref + " -omat " + xfm +\
              " -cost mutualinfo -bins 256 -dof 12 -searchrx -180 180" +\
              " -searchry -180 180 -searchrz -180 180"
        print "Executing: " + cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()
        pass

    def applyxfm(self, inp, ref, xfm, aligned):
        """
        Aligns two images with a given transform

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned as a nifti image file
                ref:
                    - Image being aligned to as a nifti image file
                xfm:
                    - Transform between two images
                aligned:
                    - Aligned output image as a nifti image file
        """
        cmd = "flirt -in " + inp + " -ref " + ref + " -out " + aligned +\
              " -init " + xfm + " -interp trilinear -applyxfm"

        print "Executing: " + cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()
        pass

    def align_slices(self, dti, corrected_dti, idx):
        """
        Performs eddy-correction (or self-alignment) of a stack of 3D images

        **Positional Arguments:**
                dti:
                    - 4D (DTI) image volume as a nifti file
                corrected_dti:
                    - Corrected and aligned DTI volume in a nifti file
                idx:
                    - Index of the first B0 volume in the stack
        """
        cmd = "eddy_correct " + dti + " " + corrected_dti + " " + str(idx)
        print "Executing: " + cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()
        pass

    def dti2atlas(self, dti, gtab, mprage, atlas, aligned_dti, outdir):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                dti:
                    - Input impage to be aligned as a nifti image file
                bvals:
                    - File containing list of bvalues for each scan
                bvecs:
                    - File containing gradient directions for each scan
                mprage:
                    - Intermediate image being aligned to as a nifti image file
                atlas:
                    - Terminal image being aligned to as a nifti image file
                aligned_dti:
                    - Aligned output dti image as a nifti image file
        """
        # Creates names for all intermediate files used
        # GK TODO: come up with smarter way to create these temp file names
        dti_name = op.splitext(op.splitext(op.basename(dti))[0])[0]
        mprage_name = op.splitext(op.splitext(op.basename(mprage))[0])[0]
        atlas_name = op.splitext(op.splitext(op.basename(atlas))[0])[0]

        dti2 = outdir + "/tmp/" + dti_name + "_t2.nii.gz"
        b0 = outdir + "/tmp/" + dti_name + "_b0.nii.gz"
        xfm1 = outdir + "/tmp/" + dti_name + "_" + mprage_name + "_xfm.mat"
        xfm2 = outdir + "/tmp/" + mprage_name + "_" + atlas_name + "_xfm.mat"
        xfm3 = outdir + "/tmp/" + dti_name + "_" + atlas_name + "_xfm.mat"

        # Align DTI volumes to each other
        self.align_slices(dti, dti2, np.where(gtab.b0s_mask)[0])

        # Loads DTI image in as data and extracts B0 volume
        import ndmg.utils as mgu
        dti_im = nb.load(dti2)
        b0_im = mgu().get_b0(gtab, dti_im.get_data())
        # GK TODO: why doesn't top import work?

        # Wraps B0 volume in new nifti image
        b0_head = dti_im.get_header()
        b0_head.set_data_shape(b0_head.get_data_shape()[0:3])
        b0_out = nb.Nifti1Image(b0_im, affine=dti_im.get_affine(),
                                header=b0_head)
        b0_out.update_header()
        nb.save(b0_out, b0)

        # Algins B0 volume to MPRAGE, and MPRAGE to Atlas
        self.align(b0, mprage, xfm1)
        self.align(mprage, atlas, xfm2)

        # Combines transforms from previous registrations in proper order
        cmd = "convert_xfm -omat " + xfm3 + " -concat " + xfm2 + " " + xfm1
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        p.communicate()

        # Applies combined transform to dti image volume
        self.applyxfm(dti2, atlas, xfm3, aligned_dti)
