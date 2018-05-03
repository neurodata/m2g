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
# Edited by Eric Bridgeford.
# Email: gkiar@jhu.edu

from subprocess import Popen, PIPE
import os.path as op
import ndmg.utils as mgu
from ndmg.utils import reg_utils as mgru
from ndmg.utils import nuis_utils as mgnu
import nibabel as nb
import numpy as np
import nilearn.image as nl
from ndmg.stats.func_qa_utils import registration_score


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
              bins=256, interp=None, cost="mutualinfo", sch=None,
              wmseg=None, init=None):
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
                    - the interpolation method to use.
                sch:
                    - the optional FLIRT schedule file.
                wmseg:
                    - an optional white-matter segmentation for bbr.
                init:
                    - an initial guess of an alignment.
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
        if sch is not None:
            cmd += " -schedule {}".format(sch)
        if wmseg is not None:
            cmd += " -wmseg {}".format(wmseg)
        if init is not None:
            cmd += " -init {}".format(init)
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
        # if we are doing fnirt, use predefined fnirt config file
        # since the config is most robust
        cmd = "fnirt --in={} --aff={} --cout={} --ref={}"
        cmd += " --config=T1_2_MNI152_2mm"
        cmd = cmd.format(inp, xfm, warp, ref)
        if mask is not None:
            cmd += " --refmask={}".format(mask)
        out, err = mgu.execute_cmd(cmd, verb=True)

    def applyxfm(self, inp, ref, xfm, aligned, interp='trilinear'):
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
            interp:
                - the interpolation method to use from fsl.
        """
        cmd = "flirt -in {} -ref {} -out {} -init {} -interp {} -applyxfm"
        cmd = cmd.format(inp, ref, aligned, xfm, interp)
        mgu.execute_cmd(cmd, verb=True)

    def apply_warp(self, inp, ref, out, warp=None, xfm=None, mask=None):
        """
        Applies a warp from the input to reference space
        in a single step, using information about the structural->ref
        mapping as well as the epi to structural mapping.

        **Positional Arguments:**

            inp:
                - the input image to be aligned as a nifti image file.
            out:
                - the output aligned image.
            ref:
                - the image being aligned to.
            warp:
                - the warp from the structural to reference space.
            xfm:
                - the affine transformation to apply to the input.
            mask:
                - the mask to extract around after applying the transform.
        """
        cmd = "applywarp --ref={} --in={} --out={}".format(ref, inp, out)
        if warp is not None:
            cmd += " --warp={}".format(warp)
        if xfm is not None:
            cmd += " --premat={}".format(xfm)
        if mask is not None:
            cmd += " --mask={}".format(mask)
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


class epi_register(register):
    def __init__(self, epi, t1w, t1w_brain, atlas, atlas_brain, atlas_mask,
                 aligned_epi, aligned_t1w, outdir):
        """
        A class to change brain spaces from a subject's epi sequence
        to that of a standardized atlas.

        **Positional Arguments:**

            epi:
                - the path of the preprocessed fmri image.
            t1w:
                - the path of the T1w scan.
            t1w_brain:
                - the path of the brain extracted T1w scan.
            atlas:
                - the template atlas.
            atlas_brain:
                - the template brain.
            atlas_mask:
                - the template mask.
            aligned_epi:
                - the name of the aligned fmri scan to produce.
            aligned_t1w:
                - the name of the aligned anatomical scan to produce
            outdir:
                - the output base directory.
        """
        super(register, self).__init__()

        # for naming temporary files
        self.epi_name = mgu.get_filename(epi)
        self.t1w_name = mgu.get_filename(t1w)
        self.atlas_name = mgu.get_filename(atlas)

        # our basic dependencies
        self.epi = epi
        self.t1w = t1w
        self.t1w_brain = t1w_brain
        self.atlas = atlas
        self.atlas_brain = atlas_brain
        self.atlas_mask = atlas_mask
        self.taligned_epi = aligned_epi
        self.taligned_t1w = aligned_t1w
        self.outdir = outdir
        t1w_skull = "{}/{}_temp-aligned_skull.nii.gz"
        self.taligned_t1w_skull = t1w_skull.format(self.outdir['reg_a'],
                                                   self.t1w_name)
        # strategies for qa later
        self.sreg_strat = None
        self.treg_strat = None

        # if we do bbr, then we will need a wm mask, so store for qa
        self.wm_mask = None

        if sum(nb.load(t1w).header.get_zooms()) <= 6:
            self.simple = False
        else:
            self.simple = True  # if the input is poor
        # name intermediates for self-alignment
        self.saligned_xfm = "{}/{}_self-aligned.mat".format(
            self.outdir['reg_m'],
            self.epi_name)
        pass

    def self_align(self):
        """
        A function to perform self alignment. Uses a local optimisation
        cost function to get the two images close, and then uses bbr
        to obtain a good alignment of brain boundaries.
        """
        xfm_init1 = "{}/{}_xfm_epi2t1w_init1.mat".format(self.outdir['reg_m'],
                                                         self.epi_name)
        xfm_init2 = "{}/{}_xfm_epi2t1w_init2.mat".format(self.outdir['reg_m'],
                                                         self.epi_name)
        epi_init = "{}/{}_local.nii.gz".format(self.outdir['reg_m'],
                                               self.epi_name)

        # perform an initial alignment with a gentle translational guess
        # note that this schedule file only adjusts such that the x, y, z
        # params between the epi and the t1w brain are optimal
        self.align(self.epi, self.t1w_brain, xfm=xfm_init1, bins=None,
                   dof=None, cost=None, searchrad=None,
                   sch="${FSLDIR}/etc/flirtsch/sch3Dtrans_3dof")
        # perform a near local-only registration, which looks for local
        # fits of the voxels and will improve our registration if our
        # image is for instance cut off somewhere with simple3d
        # make sure to initialize with our translationally optimal fit
        self.align(self.epi, self.t1w_brain, xfm=xfm_init2, init=xfm_init1,
                   bins=None, dof=None, cost=None, searchrad=None,
                   out=epi_init, sch="${FSLDIR}/etc/flirtsch/simple3D.sch")

        # if we have a quality T1w image (resolution < 2x2x2) we will get
        # a decent segmentation, and then we can use bbr from flirt
        if not self.simple:
            xfm_init3 = "{}/{}_xfm_epi2t1w.mat".format(self.outdir['reg_m'],
                                                       self.epi_name)
            xfm_bbr = "{}/{}_xfm_bbr.mat".format(self.outdir['reg_m'],
                                                 self.epi_name)
            epi_bbr = "{}/{}_bbr.nii.gz".format(self.outdir['reg_m'],
                                                self.epi_name)
            # use a 6 dof registration with near-local initializer
            self.align(self.epi, self.t1w_brain, xfm=xfm_init3,
                       init=xfm_init2, bins=None, dof=6, cost=None,
                       searchrad=None, sch=None)
            # segment the t1w brain into probability maps
            map_path = "{}/{}_t1w_seg".format(self.outdir['reg_a'],
                                              self.t1w_name)
            maps = mgnu.segment_t1w(self.t1w_brain, map_path)
            wm_mask = "{}/{}_wmm.nii.gz".format(self.outdir['reg_a'],
                                                self.t1w_name)
            self.wm_mask = wm_mask
            # use the probability maps to extract white matter mask
            mgnu.probmap2mask(maps['wm_prob'], wm_mask, 0.5)
            # perform flirt with boundary-based registration, using the
            # white matter mask to improve registration quality
            self.align(self.epi, self.t1w, xfm=xfm_bbr, wmseg=wm_mask,
                       out=epi_bbr, init=xfm_init3, interp="spline",
                       sch="${FSLDIR}/etc/flirtsch/bbr.sch")
            # store the 3d image to use as our qa image, but keep the transform
            # so that we don't have to multiply yet
            self.sreg_xfm = xfm_bbr
            self.sreg_brain = epi_bbr
            self.sreg_strat = 'epireg'  # store the strategy
        else:
            # if we have low quality T1w image, we will not be able
            # to segment, so do not use bbr
            print ("Warning: BBR self registration not "
                   "attempted, as input is low quality.")
            # use the 3d image and transform from the near-local registration
            # instead
            self.sreg_xfm = xfm_init2
            self.sreg_brain = epi_init
            self.sreg_strat = 'flirt'
        # have to use bet for this, as afni 3dautomask
        # only works on 4d volumes
        mgu.extract_brain(self.sreg_brain, self.sreg_brain,
                          opts='-f 0.3 -R')
        pass

    def template_align(self):
        """
        A function to perform template alignment. First tries nonlinear
        registration, and if that does not work effectively, does a linear
        registration instead.
        NOTE: for this to work, must first have called self-align.
        """
        xfm_t1w2temp_init = "{}/{}_xfm_t1w2temp_init.mat".format(
            self.outdir['reg_a'],
            self.t1w_name
        )
        xfm_t1w2temp = "{}/{}_xfm_t1w2temp.mat".format(self.outdir['reg_a'],
                                                       self.t1w_name)

        # linear registration initializer with local optimisation in
        # case our brain extraction is poor to give our 12 dof flirt
        # a better starting point
        # if brain extraction fails, a 12 dof registration will perform
        # horribly since the brain will be an odd shape, leading to total
        # failure. The idea is that local optimisation looks to essentially
        # align "regions" of the brain, and as such, will not add unnecessary
        # stretching if the brain is not the correct shape, potentially
        # leading the 12 dof registration to not totally distort the image
        self.align(self.t1w_brain, self.atlas_brain, xfm=xfm_t1w2temp_init,
                   init=None, bins=None, dof=None, cost=None, searchrad=None,
                   out=None, sch="${FSLDIR}/etc/flirtsch/sch3Dtrans_3dof") 

        # linear registration from t1 space to atlas space with a 12 dof
        # linear registration to serve as our initializer
        self.align(self.t1w_brain, self.atlas_brain, xfm=xfm_t1w2temp,
                   out=None, dof=12, searchrad=True, bins=256, interp="spline",
                   wmseg=None, init=xfm_t1w2temp_init)

        self.epi_aligned_skull = "{}/{}_temp-aligned_skull.nii.gz".format(
            self.outdir['reg_m'],
            self.epi_name
        )  # template-aligned with skull
        # if the atlas is MNI 2mm, then we have a config file for it
        if (nb.load(self.atlas).get_data().shape in [(91, 109, 91)] and
                (self.simple is False)):
            warp_t1w2temp = "{}/{}_warp_t1w2temp.nii.gz".format(
                self.outdir['reg_a'],
                self.epi_name
            )  # to store the template warp
            # use FNIRT to nonlinearly align from the t1w to the
            # template space, using the 12 dof transform as an initializer
            self.align_nonlinear(self.t1w, self.atlas, xfm_t1w2temp,
                                 warp_t1w2temp, mask=self.atlas_mask)
            # apply the warp from the epi to the atlas space by first using
            # the linear transform from the epi to the template space
            self.apply_warp(self.epi, self.atlas, self.epi_aligned_skull,
                            warp=warp_t1w2temp, xfm=self.sreg_xfm)
            # apply the warp from the t1w to the atlas space
            self.apply_warp(self.t1w, self.atlas, self.taligned_t1w_skull,
                            warp=warp_t1w2temp)
            self.treg_strat = 'fnirt'  # strategy details
        else:
            # if we dont have 2mm mni or a low quality t1w, FNIRT is unsuitable
            print "Atlas is not 2mm MNI, or input is low quality."
            print "Using linear template registration."

            xfm_epi2temp = "{}/{}_xfm_epi2temp.mat".format(
                self.outdir['reg_m'],
                self.epi_name
            )
            # just combine our 12 dof linear transform from t1w to template
            # with our transform from epi to t1w space to get a transform
            # from epi ->(-> t1w ->)-> temp space (epi -> temp)
            self.combine_xfms(xfm_t1w2temp, self.sreg_xfm, xfm_epi2temp)
            # apply linear transformation from epi to template space
            self.applyxfm(self.epi, self.atlas, xfm_epi2temp,
                          self.epi_aligned_skull, interp='spline')
            # apply 12 dof linear transform from t1w to template space
            self.apply_warp(self.t1w, self.atlas, self.taligned_t1w_skull,
                            xfm=xfm_t1w2temp)
            self.treg_strat = 'flirt'  # strategy
        # use BET to extract brain from our epi volume
        mgu.extract_brain(self.epi_aligned_skull, self.taligned_epi,
                          opts='-F')
        
        # use AFNI to extract brain from our t1w volume
        mgru.extract_t1w_brain(self.taligned_t1w_skull, self.taligned_t1w,
                               self.outdir['reg_a'])
        pass
