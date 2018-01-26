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
        resolution dwi images to a high resolution atlas.
        """
        pass

    def align(self, inp, ref, xfm=None, out=None, dof=12, searchrad=True,
              bins=256, interp=None, cost="mutualinfo"):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                inp:
                    - Input impage to be aligned as a nifti image file
                ref:
                    - Image being aligned to as a nifti image file
                xfm:
                    - Returned transform between two images
                out:
                    - determines whether the image will be automatically
                    aligned.
                dof:
                    - the number of degrees of freedom of the alignment.
                searchrad:
                    - a bool indicating whether to use the predefined
                    searchradius parameter (180 degree sweep in x, y, and z).
                interp:
                    - the interpolation method to use. Default is trilinear.
        """
        cmd = "flirt -in {} -ref {}".format(inp, ref)
        if xfm is not None:
            cmd += " -omat {}".format(xfm)
        if out is not None:
            cmd += " -out {}".format(out)
        if dof is not None:
            cmd += " -dof {}".format(dof)
        if bins is not None:
            cmd += " -bins {}".format(bins)
        if interp is not None:
            cmd += " -interp {}".format(interp)
        if cost is not None:
            cmd += " -cost {}".format(cost)
        if searchrad is not None:
            cmd += " -searchrx -180 180 -searchry -180 180 " +\
                   "-searchrz -180 180"
        mgu.execute_cmd(cmd, verb=True)

    def align_epi(self, epi, t1, brain, out):
        """
        Algins EPI images to T1w image
        """
        cmd = 'epi_reg --epi={} --t1={} --t1brain={} --out={}'
        cmd = cmd.format(epi, t1, brain, out)
        mgu.execute_cmd(cmd, verb=True)

    def align_nonlinear(self, inp, ref, xfm, warp, mask=None):
        """
        Aligns two images using nonlinear methods and stores the
        transform between them.

        **Positional Arguments:**

            inp:
                - the input image.
            ref:
                - the reference image.
            affxfm:
                - the affine transform to use.
            warp:
                - the path to store the nonlinear warp.
            mask:
                - a mask in which voxels will be extracted
                during nonlinear alignment.
        """
        cmd = "fnirt --in={} --aff={} --cout={} --ref={} --subsamp=4,2,1,1"
        cmd = cmd.format(inp, xfm, warp, ref)
        if mask is not None:
            cmd += " --refmask={}".format(mask)
        out, err = mgu.execute_cmd(cmd, verb=True)

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
        cmd = "flirt -in {} -ref {} -out {} -init {} -interp trilinear -applyxfm"
        cmd = cmd.format(inp, ref, aligned, xfm)
        mgu.execute_cmd(cmd, verb=True)

    def apply_warp(self, inp, out, ref, warp, xfm=None, mask=None):
        """
        Applies a warp from the functional to reference space
        in a single step, using information about the structural->ref
        mapping as well as the functional to structural mapping.

        **Positional Arguments:**

            inp:
                - the input image to be aligned as a nifti image file.
            out:
                - the output aligned image.
            ref:
                - the image being aligned to.
            warp:
                - the warp from the structural to reference space.
            premat:
                - the affine transformation from functional to
                structural space.
        """
        cmd = "applywarp --ref=" + ref + " --in=" + inp + " --out=" + out +\
              " --warp=" + warp
        if xfm is not None:
            cmd += " --premat=" + xfm
        if mask is not None:
            cmd += " --mask=" + mask
        mgu.execute_cmd(cmd, verb=True)

    def align_slices(self, dwi, corrected_dwi, idx):
        """
        Performs eddy-correction (or self-alignment) of a stack of 3D images

        **Positional Arguments:**
                dwi:
                    - 4D (DTI) image volume as a nifti file
                corrected_dwi:
                    - Corrected and aligned DTI volume in a nifti file
                idx:
                    - Index of the first B0 volume in the stack
        """
        cmd = "eddy_correct {} {} {}".format(dwi, corrected_dwi, idx)
        status = mgu.execute_cmd(cmd, verb=True)

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

    def resample_fsl(self, base, res, template):
        """
        A function to resample a base image in fsl to that of a template.
        **Positional Arguments:**

           base:
                - the path to the base image to resample.
            res:
                - the filename after resampling.
            template:
                - the template image to align to.
        """
        goal_res = int(nb.load(template).get_header().get_zooms()[0])
        cmd = "flirt -in {} -ref {} -out {} -nosearch -applyisoxfm {}"
        cmd = cmd.format(base, template, res, goal_res)
        mgu.execute_cmd(cmd, verb=True)

    def combine_xfms(self, xfm1, xfm2, xfmout):
        """
        A function to combine two transformations, and output the
        resulting transformation.

        **Positional Arguments**
            xfm1:
                - the path to the first transformation
            xfm2:
                - the path to the second transformation
            xfmout:
                - the path to the output transformation
        """
        cmd = "convert_xfm -omat {} -concat {} {}".format(xfmout, xfm1, xfm2)
        mgu.execute_cmd(cmd, verb=True)

    def func2atlas(self, func, t1w, atlas, atlas_brain, atlas_mask,
                   aligned_func, aligned_t1w, outdir):
        """
        A function to change coordinates from the subject's
        brain space to that of a template using nonlinear
        registration.

        **Positional Arguments:**

            fun:
                - the path of the preprocessed fmri image.
            t1w:
                - the path of the T1 scan.
            atlas:
                - the template atlas.
            atlas_brain:
                - the template brain.
            atlas_mask:
                - the template mask.
            aligned_func:
                - the name of the aligned fmri scan to produce.
            aligned_t1w:
                - the name of the aligned anatomical scan to produce
            outdir:
                - the output base directory.
       """
        func_name = mgu.get_filename(func)
        t1w_name = mgu.get_filename(t1w)
        atlas_name = mgu.get_filename(atlas)

        func2 = mgu.name_tmps(outdir, func_name, "_t1w.nii.gz")
        temp_aligned = mgu.name_tmps(outdir, func_name, "_noresamp.nii.gz")
        t1w_brain = mgu.name_tmps(outdir, t1w_name, "_brain.nii.gz")
        xfm_t1w2temp = mgu.name_tmps(outdir, func_name, "_xfm_t1w2temp.mat")

        # Applies skull stripping to T1 volume, then EPI alignment to T1
        mgu.extract_brain(t1w, t1w_brain, ' -B')
        self.align_epi(func, t1w, t1w_brain, func2)
        
        self.align(t1w_brain, atlas_brain, xfm_t1w2temp)
        # Only do FNIRT at 1mm or 2mm
        if nb.load(atlas).get_data().shape in [(182, 218, 182), (91, 109, 91)]:
            warp_t1w2temp = mgu.name_tmps(outdir, func_name,
                                          "_warp_t1w2temp.nii.gz")

            self.align_nonlinear(t1w, atlas, xfm_t1w2temp, warp_t1w2temp,
                                 mask=atlas_mask)

            self.apply_warp(func2, temp_aligned, atlas, warp_t1w2temp) 
            self.apply_warp(t1w, aligned_t1w, atlas, warp_t1w2temp,
                            mask=atlas_mask)
        else:
            self.applyxfm(func2, atlas, xfm_t1w2temp, temp_aligned)
            self.applyxfm(t1w, atlas, xfm_t1w2temp, aligned_t1w)

        self.resample(temp_aligned, aligned_func, atlas)


    def dwi2atlas(self, dwi, gtab, t1w, atlas,
                  aligned_dwi, outdir, clean=False):
        """
        Aligns two images and stores the transform between them

        **Positional Arguments:**

                dwi:
                    - Input impage to be aligned as a nifti image file
                gtab:
                    - object containing gradient directions and strength
                t1w:
                    - Intermediate image being aligned to as a nifti image file
                atlas:
                    - Terminal image being aligned to as a nifti image file
                aligned_dwi:
                    - Aligned output dwi image as a nifti image file
                outdir:
                    - Directory for derivatives to be stored
        """
        # Creates names for all intermediate files used
        dwi_name = mgu.get_filename(dwi)
        t1w_name = mgu.get_filename(t1w)
        atlas_name = mgu.get_filename(atlas)

        dwi2 = mgu.name_tmps(outdir, dwi_name, "_t2.nii.gz")
        temp_aligned = mgu.name_tmps(outdir, dwi_name, "_ta.nii.gz")
        temp_aligned2 = mgu.name_tmps(outdir, dwi_name, "_ta2.nii.gz")
        b0 = mgu.name_tmps(outdir, dwi_name, "_b0.nii.gz")
        t1w_brain = mgu.name_tmps(outdir, t1w_name, "_ss.nii.gz")
        xfm = mgu.name_tmps(outdir, t1w_name,
                            "_" + atlas_name + "_xfm.mat")

        # Align DTI volumes to each other
        self.align_slices(dwi, dwi2, np.where(gtab.b0s_mask)[0][0])

        # Loads DTI image in as data and extracts B0 volume
        dwi_im = nb.load(dwi2)
        b0_im = mgu.get_b0(gtab, dwi_im.get_data())

        # Wraps B0 volume in new nifti image
        b0_head = dwi_im.get_header()
        b0_head.set_data_shape(b0_head.get_data_shape()[0:3])
        b0_out = nb.Nifti1Image(b0_im, affine=dwi_im.get_affine(),
                                header=b0_head)
        b0_out.update_header()
        nb.save(b0_out, b0)

        # Applies skull stripping to T1 volume, then EPI alignment to T1
        mgu.extract_brain(t1w, t1w_brain, ' -B')
        self.align_epi(dwi2, t1w, t1w_brain, temp_aligned)

        # Applies linear registration from T1 to template
        self.align(t1w, atlas, xfm)

        # Applies combined transform to dwi image volume
        self.applyxfm(temp_aligned, atlas, xfm, temp_aligned2)
        self.resample(temp_aligned2, aligned_dwi, atlas)

        if clean:
            cmd = "rm -f {} {} {} {} {}*".format(dwi2, temp_aligned, b0,
                                                 xfm, t1w_name)
            print("Cleaning temporary registration files...")
            mgu.execute_cmd(cmd)
