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

# register.py
# Created by Greg Kiar on 2016-01-28.
# Email: gkiar@jhu.edu

from subprocess import Popen, PIPE
import os.path as op
import ndmg.utils as mgu
import nibabel as nb
import numpy as np
import nilearn.image as nl


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
        print("Executing: " + cmd)
        mgu.execute_cmd(cmd)
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
        cmd = "".join(["flirt -in ", inp, " -ref ", ref, " -out ", aligned,
                       " -init ", xfm, " -interp trilinear -applyxfm"])
        print("Executing: " + cmd)
        mgu.execute_cmd(cmd)
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
        print("Executing: " + cmd)
        status = mgu.execute_cmd(cmd)
        pass

    def resample(self, base, ingested, template):
        """
        Resamples the image such that images which have already been aligned
        in real coordinates also overlap in the image/voxel space.

        **Positional Arguments**
                base:
                    - Image to be aligned
                ingested:
                    - Name of image after alignment
                template:
                    - Image that is the target of the alignment
        """
        # Loads images
        template_im = nb.load(template)
        base_im = nb.load(base)
        # Aligns images
        target_im = nl.resample_img(base_im,
                                    target_affine=template_im.get_affine(),
                                    target_shape=template_im.get_data().shape,
                                    interpolation="nearest")
        # Saves new image
        nb.save(target_im, ingested)
        pass

    def dti2atlas(self, dti, gtab, mprage, atlas,
                  aligned_dti, outdir, clean=False):
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
        dti_name = mgu.get_filename(dti)
        mprage_name = mgu.get_filename(mprage)
        atlas_name = mgu.get_filename(atlas)

        dti2 = mgu.name_tmps(outdir, dti_name, "_t2.nii.gz")
        temp_aligned = mgu.name_tmps(outdir, dti_name, "_ta.nii.gz")
        temp_aligned2 = mgu.name_tmps(outdir, dti_name, "_ta2.nii.gz")
        b0 = mgu.name_tmps(outdir, dti_name, "_b0.nii.gz")
        mprage2 = mgu.name_tmps(outdir, mprage_name, "_ss.nii.gz")
        xfm = mgu.name_tmps(outdir, mprage_name,
                              "_" + atlas_name + "_xfm.mat")

        # Align DTI volumes to each other
        self.align_slices(dti, dti2, np.where(gtab.b0s_mask)[0][0])

        # Loads DTI image in as data and extracts B0 volume
        dti_im = nb.load(dti2)
        b0_im = mgu.get_b0(gtab, dti_im.get_data())

        # Wraps B0 volume in new nifti image
        b0_head = dti_im.get_header()
        b0_head.set_data_shape(b0_head.get_data_shape()[0:3])
        b0_out = nb.Nifti1Image(b0_im, affine=dti_im.get_affine(),
                                header=b0_head)
        b0_out.update_header()
        nb.save(b0_out, b0)

        # Applies skull stripping to MPRAGE volume
        cmd = 'bet ' + mprage + ' ' + mprage2 + ' -B'
        print("Executing: " + cmd)
        mgu.execute_cmd(cmd)

        # Algins B0 volume to MPRAGE, and MPRAGE to Atlas
        cmd = "".join(['epi_reg --epi=', dti2, ' --t1=', mprage,
                       ' --t1brain=', mprage2, ' --out=', temp_aligned])
        print("Executing: " + cmd)
        mgu.execute_cmd(cmd)

        self.align(mprage, atlas, xfm)

        # Applies combined transform to dti image volume
        self.applyxfm(temp_aligned, atlas, xfm, temp_aligned2)
        self.resample(temp_aligned2, aligned_dti, atlas)

        if clean:
            cmd = "".join(["rm -f ", dti2, " ", temp_aligned,
                           " ", b0, " ", xfm, " ", outdir, "/tmp/",
                           mprage_name, "*"])
            print("Cleaning temporary registration files...")
            mgu.execute_cmd(cmd)
