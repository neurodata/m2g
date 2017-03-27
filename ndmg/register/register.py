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
from ndmg.stats.qa_func import registration_score
from abc import ABCMeta, abstractmethod


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
              bins=256, interp=None, cost="mutualinfo", sch=None):
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
                sch:
                    - the optional FLIRT schedule file.
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
        cmd = "fnirt --in={} --aff={} --cout={} --ref={} --config=T1_2_MNI152_2mm"
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
            cmd = "rm -f {} {} {} {} {} {}*".format(dwi2, temp_aligned, b0,
                                                    xfm, outdir, t1w_name)
            print("Cleaning temporary registration files...")
            mgu.execute_cmd(cmd)


class func_register(register):
    def __init__(self, func, t1w, atlas, atlas_brain, atlas_mask,
                 aligned_func, aligned_t1w, outdir):
        """
        A class to change brain spaces from a subject's epi sequence
        to that of a standardized atlas.

        **Positional Arguments:**

            func:
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
        super(register, self).__init__()
        # our basic dependencies
        self.epi = func
        self.t1w = t1w
        self.atlas = atlas
        self.atlas_brain = atlas_brain
        self.atlas_mask = atlas_mask
        self.taligned_epi = aligned_func
        self.taligned_t1w = aligned_t1w
        self.outdir = outdir
        # strategies so we can iterate for qc later
        self.sreg_strat = []
        self.sreg_epi = []
        self.treg_strat = []
        self.treg_epi = []
        self.treg_t1w = []
        # for naming temporary files
        self.epi_name = mgu.get_filename(func)
        self.t1w_name = mgu.get_filename(t1w)
        self.atlas_name = mgu.get_filename(atlas)
        # since we will need the t1w brain multiple times
        self.t1w_brain = mgu.name_tmps(self.outdir, self.t1w_name,
                                       "_brain.nii.gz")
        # Applies skull stripping to T1 volume
        # using a very low sensitivity for thresholding
        bet_sens = '-f 0.3 -R -B -S'
        mgu.extract_brain(self.t1w, self.t1w_brain, opts=bet_sens)
        # name intermediates for self-alignment
        self.saligned_epi = mgu.name_tmps(self.outdir, self.epi_name,
                                          "_self-aligned.nii.gz")
        pass


    def self_align(self):
        """
        A function to perform self alignment. Uses a local optimisation
        cost function to get the two images close, and then uses bbr
        to obtain a good alignment of brain boundaries.
        """
        epi_local = mgu.name_tmps(self.outdir, self.epi_name,
                                  "_self-aligned_local.nii.gz")
        epi_bbr = mgu.name_tmps(self.outdir, self.epi_name,
                                "_self-aligned_bbr.nii.gz")
        temp_aligned = mgu.name_tmps(self.outdir, self.epi_name,
                                     "_noresamp.nii.gz")
        xfm_local = mgu.name_tmps(self.outdir, self.epi_name,
                                  "_xfm_epi2t1w_local.mat")

        # perform an initial alignment with a gentle local optimization
        self.align(self.epi, self.t1w_brain, xfm=xfm_local, bins=None,
                   dof=None, cost=None, searchrad=None,
                   sch="${FSLDIR}/etc/flirtsch/simple3D.sch")
        self.applyxfm(self.epi, self.t1w_brain, xfm_local, epi_local)

        # attempt EPI registration. note that this somethimes does not
        # work great if our EPI has a low field of view.
        self.align_epi(epi_local, self.t1w, self.t1w_brain, epi_bbr)

        print "Analyzing Self Registration Quality..."
        sc_bbr = registration_score(epi_bbr, self.t1w_brain, self.outdir)

        # if BBR worked well, it performs a much better self registration
        # so use that strategy
        if (sc_bbr[0] > 0.8):
            self.resample(epi_bbr, self.saligned_epi, self.t1w)
        else:
            print "WARNING: BBR Self registration failed."
            self.resample(epi_local, self.saligned_epi, self.t1w)
        self.sreg_strat = ['bbr', 'local']
        self.sreg_epi = [epi_bbr, epi_local]
        pass


    def template_align(self):
        """
        A function to perform template alignment. First tries nonlinear
        registration, and if that does not work effectively, does a linear
        registration instead.
        NOTE: for this to work, must first have called self-align.
        """
        xfm_t1w2temp = mgu.name_tmps(self.outdir, self.epi_name,
                                     "_xfm_t1w2temp.mat")
        # linear registration from t1 space to atlas space
        self.align(self.t1w_brain, self.atlas_brain, xfm_t1w2temp)

        # if the atlas is MNI 2mm, then we have a config file for it
        if (nb.load(self.atlas).get_data().shape in [(91, 109, 91)]):
            warp_t1w2temp = mgu.name_tmps(self.outdir, self.epi_name,
                                          "_warp_t1w2temp.nii.gz")
            epi_nl = mgu.name_tmps(self.outdir, self.epi_name,
                                   "_temp-aligned_nonlinear.nii.gz")
            t1w_nl = mgu.name_tmps(self.outdir, self.t1w_name,
                                   "_temp-aligned_nonlinear.nii.gz")
            self.align_nonlinear(self.t1w, self.atlas, xfm_t1w2temp,
                                 warp_t1w2temp, mask=self.atlas_mask)

            self.apply_warp(self.saligned_epi, epi_nl, self.atlas,
                            warp_t1w2temp)

            print "Analyzing Nonlinear Template Registration Quality..."
            sc_fnirt = registration_score(epi_nl, self.atlas_brain, self.outdir)

            self.treg_strat.insert(0, 'nonlinear')
            self.treg_epi.insert(0, epi_nl)
            self.treg_t1w.insert(0, t1w_nl)
            # if self registration does well, return. else, use linear
            if (sc_fnirt[0] > 0.8):
                self.apply_warp(self.t1w, t1w_nl, self.atlas,
                                warp_t1w2temp, mask=self.atlas_mask)
                self.resample(t1w_nl, self.taligned_t1w, self.atlas)
                self.resample(epi_nl, self.taligned_epi, self.atlas)
                return
            else:
                print "WARNING: Error using FNIRT."
        else:
            print "Atlas is not 2mm MNI. Using linear template registration."

        # note that if Nonlinear failed, we will come here as well
        epi_lin = mgu.name_tmps(self.outdir, self.epi_name,
                                "_temp-aligned_linear.nii.gz")
        t1w_lin = mgu.name_tmps(self.outdir, self.t1w_name,
                                "_temp-aligned_linear.nii.gz") 
        self.treg_strat.insert(0, 'linear')
        self.treg_epi.insert(0, epi_lin)
        self.treg_t1w.insert(0, t1w_lin)
        # just apply our previously computed linear transform
        self.applyxfm(self.saligned_epi, self.atlas, xfm_t1w2temp, epi_lin)
        self.applyxfm(self.t1w, self.atlas, xfm_t1w2temp, t1w_lin)
        self.resample(t1w_lin, self.taligned_t1w, self.atlas)
        self.resample(epi_lin, self.taligned_epi, self.atlas)
        pass


    def register(self):
        """
        A function to perform self registration followed by
        template registration.
        """
        self.self_align()
        self.template_align()
        pass
