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
import ndmg.utils.utils as mgu
import nibabel as nb
import numpy as np
import nilearn.image as nl
import dipy.align.reslice as dr
from ndmg.stats import qc as mgqc


class register(object):

    def __init__(self):
        """
        Enables registration of single images to one another as well as volumes
        within multi-volume image stacks. Has options to compute transforms,
        apply transforms, as well as a built-in method for aligning low
        resolution dti images to a high resolution atlas.
        """
        import ndmg.utils as mgu
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
        cmd = "flirt -in " + inp + " -ref " + ref
        if xfm is not None:
            cmd += " -omat " + xfm
        if out is not None:
            cmd += " -out " + out
        if dof is not None:
            cmd += " -dof " + str(dof)
        if bins is not None:
            cmd += " -bins " + str(bins)
        if interp is not None:
            cmd += " -interp " + str(interp)
        if cost is not None:
            cmd += " -cost " + str(cost)
        if searchrad is not None:
            cmd += " -searchrx -180 180 -searchry -180 180 " +\
                   "-searchrz -180 180"
        mgu().execute_cmd(cmd)
        pass

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
        cmd = "fnirt --in=" + inp + " --aff=" + xfm + " --cout=" +\
              warp + " --ref=" + ref + " --subsamp=4,2,1,1"
        if mask is not None:
            cmd += " --refmask=" + mask
        status = mgu().execute_cmd(cmd)
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
        mgu().execute_cmd(cmd)
        pass

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

        mgu().execute_cmd(cmd)
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
        status = mgu().execute_cmd(cmd)
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

    def resample_ant(self, base, res, template):
        """
        A function to resample a base image to that of a template image
        using dipy.
        NOTE: Dipy is far superior for antisotropic -> isotropic
            resampling.

        **Positional Arguments:**

            base:
                - the path to the base image to resample.
            res:
                - the filename after resampling.
            template:
                - the template image to align to.
        """
        print("Resampling " + str(base) + " to " + str(template) + "...")
        baseimg = nb.load(base)
        tempimg = nb.load(template)
        data2, affine2 = dr.reslice(baseimg.get_data(),
                                    baseimg.get_affine(),
                                    baseimg.get_header().get_zooms()[:3],
                                    tempimg.get_header().get_zooms()[:3])
        img2 = nb.Nifti1Image(data2, affine2)
        nb.save(img2, res)
        pass

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
        cmd = "flirt -in " + base + " -ref " + template + " -out " +\
              res + " -nosearch -applyisoxfm " + str(goal_res)
        mgu().execute_cmd(cmd)
        pass

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
        cmd = "convert_xfm -omat " + xfmout + " -concat " + xfm1 + " " + xfm2
        mgu().execute_cmd(cmd)
        pass

    def fmri2atlas(self, mri, anat, atlas, atlas_brain, atlas_mask,
                   aligned_mri, aligned_anat, outdir, qcdir=None):
        """
        A function to change coordinates from the subject's
        brain space to that of a template using nonlinear
        registration.

        **Positional Arguments:**

            mri:
                - the path of the preprocessed mri image.
            anat:
                - the path of the raw anatomical scan.
            atlas:
                - the template atlas.
            atlas_brain:
                - the template brain.
            atlas_mask:
                - the template mask.
            aligned_mri:
                - the name of the aligned mri scan to produce.
            aligned_anat:
                - the name of the aligned anatomical scan to
                produce
            outdir:
                - the output base directory.
            qcdir:
                - the quality control directory. If None, then
                no QC will be performed.
       """
        mri_name = mgu().get_filename(mri)
        anat_name = mgu().get_filename(anat)
        atlas_name = mgu().get_filename(atlas)

        s0 = mgu().name_tmps(outdir, mri_name, "_0slice.nii.gz")
        s0_brain = mgu().name_tmps(outdir, mri_name, "_0slice_brain.nii.gz")
        anat_brain = mgu().name_tmps(outdir, mri_name, "_anat_brain.nii.gz")
        xfm_func2mpr = mgu().name_tmps(outdir, mri_name, "_xfm_func2mpr.mat")
        xfm_mpr2temp = mgu().name_tmps(outdir, mri_name, "_xfm_mpr2temp.mat")
        warp_mpr2temp = mgu().name_tmps(outdir, mri_name,
                                        "_warp_mpr2temp.nii.gz")


        mgu().get_slice(mri, 0, s0)  # get the 0 slice and save
        # extract the anatomical brain
        mgu().extract_brain(anat, anat_brain)
        # extract the brain from the s0 image
        mgu().extract_brain(s0, s0_brain)
        # align the anatomical brain to the s0 brain
        self.align(s0_brain, anat_brain, xfm_func2mpr, bins=None)
        # align the anatomical high-res brain to the high-res atlas_brain
        # this linear transformation gives us a starting point for
        # our nonlinear transformations
        self.align(anat_brain, atlas_brain, xfm_mpr2temp, bins=None)
        # align the anatomical image to the atlas image using
        # the linear alignment as a starting guess. extract over atlas_brain.
        self.align_nonlinear(anat, atlas, xfm_mpr2temp,
                             warp_mpr2temp, mask=atlas_mask)
        # apply the warp obtained from anat -> atlas to the fmri stack.
        self.apply_warp(mri, aligned_mri, atlas, warp_mpr2temp,
                        xfm=xfm_func2mpr)
        # apply the warp back to the anatomical image for quality control.
        self.apply_warp(anat, aligned_anat, atlas, warp_mpr2temp,
                        mask=atlas_mask)

        if qcdir is not None:
            mgqc().check_alignments(mri, aligned_mri, atlas, qcdir,
                                    mri_name, title="Registration")
            mgqc().image_align(aligned_mri, atlas_brain, qcdir,
                               scanid=mri_name, refid=atlas_name)
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
        dti_name = mgu().get_filename(dti)
        mprage_name = mgu().get_filename(mprage)
        atlas_name = mgu().get_filename(atlas)

        dti2 = mgu().name_tmps(outdir, dti_name, "_t2.nii.gz")
        temp_aligned = mgu().name_tmps(outdir, dti_name, "_ta.nii.gz")
        temp_aligned2 = mgu().name_tmps(outdir, dti_name, "_ta2.nii.gz")
        b0 = mgu().name_tmps(outdir, dti_name, "_b0.nii.gz")
        mprage2 = mgu().name_tmps(outdir, mprage_name, "_ss.nii.gz")
        xfm = mgu().name_tmps(outdir, mprage_name,
                              "_" + atlas_name + "_xfm.mat")

        # Align DTI volumes to each other
        self.align_slices(dti, dti2, np.where(gtab.b0s_mask)[0])

        # Loads DTI image in as data and extracts B0 volume
        dti_im = nb.load(dti2)
        b0_im = mgu().get_b0(gtab, dti_im.get_data())

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
        mgu().execute_cmd(cmd)

        # Algins B0 volume to MPRAGE, and MPRAGE to Atlas
        cmd = "".join(['epi_reg --epi=', dti2, ' --t1=', mprage,
                       ' --t1brain=', mprage2, ' --out=', temp_aligned])
        print("Executing: " + cmd)
        mgu().execute_cmd(cmd)

        self.align(mprage, atlas, xfm=xfm)

        # Applies combined transform to dti image volume
        self.applyxfm(temp_aligned, atlas, xfm, temp_aligned2)
        self.resample(temp_aligned2, aligned_dti, atlas)

        if clean:
            cmd = "".join(["rm -f ", dti2, " ", temp_aligned,
                           " ", b0, " ", xfm, " ", outdir, "/tmp/",
                           mprage_name, "*"])
            print("Cleaning temporary registration files...")
            mgu().execute_cmd(cmd)
