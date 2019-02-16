#!/usr/bin/env python -W ignore::DeprecationWarning

# Copyright 2019 NeuroData (http://neurodata.io)
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
# Repackaged for native space registrations by Derek Pisner on 2019-01-16
# Email: dpisner@utexas.edu.
# epi_register created by Eric Bridgeford.

from __future__ import print_function
import warnings
warnings.simplefilter("ignore")
import os
import nibabel as nib
from nilearn.image import load_img, math_img, resample_img, mean_img, new_img_like
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
try:
    FSLDIR = os.environ['FSLDIR']
except KeyError:
    print('FSLDIR environment variable not set!')
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgru


class dmri_reg(object):

    def __init__(self, namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple):
        self.simple = simple
        self.nodif_B0 = nodif_B0
	self.nodif_B0_mask = nodif_B0_mask
        self.t1w = t1w_in
        self.vox_size = vox_size
        self.t1w_name = 't1w'
        self.dwi_name = 'dwi'
	self.namer = namer
        self.t12mni_xfm_init = "{}/xfm_t1w2mni_init.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.t12mni_xfm = "{}/xfm_t1w2mni.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.mni2t1_xfm = "{}/xfm_mni2t1.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.mni2t1w_warp = "{}/mni2t1w_warp.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.warp_t1w2mni = "{}/warp_t12mni.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.t1w2dwi = "{}/{}_in_dwi.nii.gz".format(self.namer.dirs['output']['reg_anat'], self.t1w_name)
        self.t1_aligned_mni = "{}/{}_aligned_mni.nii.gz".format(self.namer.dirs['output']['prep_anat'], self.t1w_name)
        self.t1w_brain = "{}/{}_brain.nii.gz".format(self.namer.dirs['output']['prep_anat'], self.t1w.split('.nii.gz')[0].split('/')[-1])
        self.dwi2t1w_xfm = "{}/dwi2t1w_xfm.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.t1w2dwi_xfm = "{}/t1w2dwi_xfm.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.t1w2dwi_bbr_xfm = "{}/t1w2dwi_bbr_xfm.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.dwi2t1w_bbr_xfm = "{}/dwi2t1w_bbr_xfm.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.t1wtissue2dwi_xfm = "{}/t1wtissue2dwi_xfm.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.xfm_atlas2t1w_init = "{}/{}_xfm_atlas2t1w_init.mat".format(self.namer.dirs['tmp']['reg_m'], self.t1w_name)
        self.xfm_atlas2t1w = "{}/{}_xfm_atlas2t1w.mat".format(self.namer.dirs['tmp']['reg_m'], self.t1w_name)
        self.temp2dwi_xfm = "{}/{}_xfm_temp2dwi.mat".format(self.namer.dirs['tmp']['reg_m'], self.dwi_name)
        self.input_mni = "%s%s%s%s" % (FSLDIR, '/data/standard/MNI152_T1_', vox_size,'_brain.nii.gz')
        self.temp2dwi_xfm = "{}/{}_xfm_temp2dwi.mat".format(self.namer.dirs['tmp']['reg_m'], self.dwi_name)
        self.map_path = "{}/{}_seg".format(self.namer.dirs['output']['prep_anat'], self.t1w_name)
        self.wm_mask = "{}/{}_wm.nii.gz".format(self.namer.dirs['output']['prep_anat'], self.t1w_name)
        self.csf_mask = "{}/{}_csf.nii.gz".format(self.namer.dirs['output']['prep_anat'], self.t1w_name)
        self.gm_mask = "{}/{}_gm.nii.gz".format(self.namer.dirs['output']['prep_anat'], self.t1w_name)
        self.xfm_roi2mni_init = "{}/roi_2_mni.mat".format(self.namer.dirs['tmp']['reg_m'])
        self.lvent_out_file = "{}/LVentricle.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.rvent_out_file = "{}/RVentricle.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.mni_vent_loc = "{}/VentricleMask.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.csf_mask_dwi = "{}/{}_csf_mask_dwi.nii.gz".format(self.namer.dirs['output']['reg_anat'], self.t1w_name)
        self.gm_in_dwi = "{}/{}_gm_in_dwi.nii.gz".format(self.namer.dirs['output']['reg_anat'], self.t1w_name)
        self.vent_csf_in_dwi = "{}/{}_vent_csf_in_dwi.nii.gz".format(self.namer.dirs['output']['reg_anat'], self.t1w_name)
        self.vent_csf_in_dwi_bin = "{}/{}_vent_csf_in_dwi_bin.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
        self.vent_mask_dwi = "{}/{}_vent_mask_dwi.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
        self.vent_mask_mni = "{}/vent_mask_mni.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.vent_mask_t1w = "{}/vent_mask_t1w.nii.gz".format(self.namer.dirs['tmp']['reg_a'])
        self.wm_in_dwi = "{}/{}_wm_in_dwi.nii.gz".format(self.namer.dirs['output']['reg_anat'], self.t1w_name)
        self.wm_in_dwi_bin = "{}/{}_wm_in_dwi_bin.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
        self.wm_in_dwi_binv = "{}/{}_wm_in_dwi_binv.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
        self.mni_atlas = "%s%s%s%s" % (FSLDIR, '/data/atlases/HarvardOxford/HarvardOxford-sub-prob-', vox_size, '.nii.gz')
        self.input_mni = "%s%s%s%s" % (FSLDIR, '/data/standard/MNI152_T1_', vox_size, '_brain.nii.gz')
        self.gm_in_dwi_bin = "{}/{}_gm_in_dwi_bin.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
        self.gm_in_dwi_binv = "{}/{}_gm_in_dwi_binv.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.t1w_name)
	self.wm_gm_int_in_dwi = "{}/{}_wm_gm_int_in_dwi.nii.gz".format(namer.dirs['output']['reg_anat'], self.t1w_name)

    def gen_tissue(self):
        # BET needed for this, as afni 3dautomask only works on 4d volumes
        print('Extracting brain from raw T1w image...')
        mgru.t1w_skullstrip(self.t1w, self.t1w_brain)

        # Segment the t1w brain into probability maps
        self.maps = mgru.segment_t1w(self.t1w_brain, self.map_path)

        # Use the probability maps to extract white matter mask
        mgru.probmap2mask(self.maps['wm_prob'], self.wm_mask, 0.5)
        mgru.probmap2mask(self.maps['gm_prob'], self.gm_mask, 0.3)
        mgru.probmap2mask(self.maps['csf_prob'], self.csf_mask, 0.3)
        return

    def t1w2dwi_align(self):
        """
        alignment from T1w --> MNI and T1w_MNI --> DWI
        A function to perform self alignment. Uses a local optimisation
        cost function to get the two images close, and then uses bbr
        to obtain a good alignment of brain boundaries.
        Assumes input dwi is already preprocessed and brain extracted.
        """

        # Create linear transform/ initializer T1w-->MNI
        mgru.align(self.t1w_brain, self.input_mni, xfm=self.t12mni_xfm_init, bins=None, interp="spline", out=None, dof=12, cost='mutualinfo', searchrad=True, sch=None)

        # Attempt non-linear registration of T1 to MNI template
        if self.simple is False:
            try:
                print('Running non-linear registration: T1w-->MNI ...')
                # Use FNIRT to nonlinearly align T1 to MNI template
                mgru.align_nonlinear(self.t1w_brain, self.input_mni, xfm=self.t12mni_xfm_init, out=self.t1_aligned_mni, warp=self.warp_t1w2mni, mask=None)

                # Get warp from MNI -> T1
                mgru.inverse_warp(self.t1w_brain, self.mni2t1w_warp, self.warp_t1w2mni)
            except RuntimeError('FNIRT failed!'):
                pass
        else:
            # Falling back to linear registration
            mgru.align(self.t1w_brain, self.input_mni, xfm=self.t12mni_xfm, init=self.t12mni_xfm_init, bins=None, dof=12, cost='mutualinfo', searchrad=True, interp="spline", out=self.t1_aligned_mni, sch=None)

        # Align T1w-->DWI
        mgru.align(self.nodif_B0, self.t1w_brain, xfm=self.t1w2dwi_xfm, bins=None, interp="spline", dof=7, cost='mutualinfo', out=None, searchrad=True, sch=None)
        cmd = 'convert_xfm -omat ' + self.dwi2t1w_xfm + ' -inverse ' + self.t1w2dwi_xfm
        os.system(cmd)

        if self.simple is False:
            # Flirt bbr
            try:
		print('Running FLIRT BBR registration: T1w-->DWI ...')
                mgru.align(self.nodif_B0, self.t1w_brain, wmseg=self.wm_mask, xfm=self.dwi2t1w_bbr_xfm, init=self.dwi2t1w_xfm, bins=256, dof=7, searchrad=True, interp="spline", out=None, cost='bbr', finesearch=5, sch="${FSLDIR}/etc/flirtsch/bbr.sch")
                cmd = 'convert_xfm -omat ' + self.t1w2dwi_bbr_xfm + ' -inverse ' + self.dwi2t1w_bbr_xfm
                os.system(cmd)

                # Apply the alignment
                mgru.align(self.t1w_brain, self.nodif_B0, init=self.t1w2dwi_bbr_xfm, xfm=self.t1wtissue2dwi_xfm, bins=None, interp="spline", dof=7, cost='mutualinfo', out=self.t1w2dwi, searchrad=True, sch=None)
            except RuntimeError('FLIRT BBR failed!'):
                pass
        else:
            # Apply the alignment
            mgru.align(self.t1w_brain, self.nodif_B0, init=self.t1w2dwi_xfm, xfm=self.t1wtissue2dwi_xfm, bins=None, interp="spline", dof=7, cost='mutualinfo', out=self.t1w2dwi, searchrad=True, sch=None)

        return

    def atlas2t1w2dwi_align(self, atlas):
        """
        alignment from atlas --> T1 --> dwi
        A function to perform atlas alignment.
        Tries nonlinear registration first, and if that fails,
        does a linear registration instead.
        NOTE: for this to work, must first have called t1w2dwi_align.
        """
        self.atlas = atlas
        self.atlas_name = self.atlas.split('/')[-1].split('.')[0]
        self.aligned_atlas_skull = "{}/{}_aligned_atlas_skull.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.atlas_name)
        self.dwi_aligned_atlas = "{}/{}_aligned_atlas.nii.gz".format(self.namer.dirs['tmp']['reg_a'], self.atlas_name)
        #self.dwi_aligned_atlas_mask = "{}/{}_aligned_atlas_mask.nii.gz".format(self.outdir['reg_a'], self.atlas_name)

        if (nib.load(self.atlas).get_data().shape in [(91, 109, 91), (182, 218, 182)] and (self.simple is False)):
            try:
		# Apply warp resulting from the inverse of T1w-->MNI created earlier
                mgru.apply_warp(self.t1w_brain, self.atlas, self.aligned_atlas_skull, warp=self.mni2t1w_warp)
	
                # Apply transform to dwi space
		if self.simple is False:
		    mgru.applyxfm(self.nodif_B0, self.aligned_atlas_skull, self.t1wtissue2dwi_xfm, self.dwi_aligned_atlas)
		else:
                    mgru.applyxfm(self.nodif_B0, self.aligned_atlas_skull, self.t1wtissue2dwi_xfm, self.dwi_aligned_atlas)
            except:
                print("Atlas is not in correct dimensions, or input is low quality,\nusing linear template registration.")

                # Create transform to align atlas to T1w using flirt
                mgru.align(self.atlas, self.t1w_brain, xfm=self.xfm_atlas2t1w_init, init=None, bins=None, dof=6, cost='mutualinfo', searchrad=True, interp="spline", out=None, sch=None)
                mgru.align(self.atlas, self.t1_aligned_mni, xfm=self.xfm_atlas2t1w, out=None, dof=6, searchrad=True, bins=None, interp="spline", cost='mutualinfo', wmseg=None, init=self.xfm_atlas2t1w_init)

                # Combine our linear transform from t1w to template with our transform from dwi to t1w space to get a transform from atlas ->(-> t1w ->)-> dwi
                mgru.combine_xfms(self.xfm_atlas2t1w, self.t1wtissue2dwi_xfm, self.temp2dwi_xfm)

                # Apply linear transformation from template to dwi space
                mgru.applyxfm(self.nodif_B0, self.atlas, self.temp2dwi_xfm, self.dwi_aligned_atlas)
        else:
            # Create transform to align atlas to T1w using flirt
            mgru.align(self.atlas, self.t1w_brain, xfm=self.xfm_atlas2t1w_init, init=None, bins=None, dof=6, cost='mutualinfo', searchrad=None, interp="spline", out=None, sch=None)
            mgru.align(self.atlas, self.t1w_brain, xfm=self.xfm_atlas2t1w, out=None, dof=6, searchrad=True, bins=None, interp="spline", cost='mutualinfo', wmseg=None, init=self.xfm_atlas2t1w_init)

            # Combine our linear transform from t1w to template with our transform from dwi to t1w space to get a transform from atlas ->(-> t1w ->)-> dwi
            mgru.combine_xfms(self.xfm_atlas2t1w, self.t1wtissue2dwi_xfm, self.temp2dwi_xfm)

            # Apply linear transformation from template to dwi space
            mgru.applyxfm(self.nodif_B0, self.atlas, self.temp2dwi_xfm, self.dwi_aligned_atlas)

        # Set intensities to int
        self.atlas_img = nib.load(self.dwi_aligned_atlas)
        self.atlas_data = self.atlas_img.get_data()
        nib.save(nib.Nifti1Image(self.atlas_data.astype('int'), affine=self.atlas_img.affine, header=self.atlas_img.header), self.dwi_aligned_atlas)
        cmd='fslmaths ' + self.dwi_aligned_atlas + ' -mas ' + self.nodif_B0_mask + ' ' + self.dwi_aligned_atlas
        os.system(cmd)
        return self.dwi_aligned_atlas

    def tissue2dwi_align(self):
        """
        alignment of ventricle ROI's from MNI space --> dwi and
        CSF from T1w space --> dwi
        A function to generate and perform dwi space alignment of avoidance/waypoint masks for tractography.
        First creates ventricle ROI. Then creates transforms from stock MNI template to dwi space.
        NOTE: for this to work, must first have called both t1w2dwi_align and atlas2t1w2dwi_align.
        """

        # Create MNI-space ventricle mask
        print('Creating MNI-space ventricle ROI...')
        if not os.path.isfile(self.mni_atlas):
            raise ValueError('FSL atlas for ventricle reference not found!')
        cmd='fslroi ' + self.mni_atlas + ' ' + self.rvent_out_file + ' 2 1'
        os.system(cmd)
        cmd='fslroi ' + self.mni_atlas + ' ' + self.lvent_out_file + ' 13 1'
        os.system(cmd)
        self.args = "%s%s%s" % (' -add ', self.rvent_out_file, ' -thr 0.1 -bin -dilF ')
        cmd='fslmaths ' + self.lvent_out_file + self.args + self.mni_vent_loc
        os.system(cmd)

        # Create transform to MNI atlas to T1w using flirt. This will be use to transform the ventricles to dwi space.
        mgru.align(self.mni_atlas, self.input_mni, xfm=self.xfm_roi2mni_init, init=None, bins=None, dof=6, cost='mutualinfo', searchrad=True, interp="spline", out=None, sch="${FSLDIR}/etc/flirtsch/sch3Dtrans_3dof")

        # Create transform to align roi to mni and T1w using flirt
        mgru.applyxfm(self.input_mni, self.mni_vent_loc, self.xfm_roi2mni_init, self.vent_mask_mni)

        if self.simple is False:
            # Apply warp resulting from the inverse MNI->T1w created earlier
            mgru.apply_warp(self.t1w_brain, self.vent_mask_mni, self.vent_mask_t1w, warp=self.mni2t1w_warp)
            
	# Applyxfm tissue maps to dwi space
        mgru.applyxfm(self.nodif_B0, self.vent_mask_t1w, self.t1wtissue2dwi_xfm, self.vent_mask_dwi)
        mgru.applyxfm(self.nodif_B0, self.csf_mask, self.t1wtissue2dwi_xfm, self.csf_mask_dwi)
        mgru.applyxfm(self.nodif_B0, self.gm_mask, self.t1wtissue2dwi_xfm, self.gm_in_dwi)
        mgru.applyxfm(self.nodif_B0, self.wm_mask, self.t1wtissue2dwi_xfm, self.wm_in_dwi)	

        # Threshold WM to binary in dwi space
        self.t_img = load_img(self.wm_in_dwi)
        self.mask = math_img('img > 0', img=self.t_img)
        self.mask.to_filename(self.wm_in_dwi_bin)

        # Threshold GM to binary in dwi space
        self.t_img = load_img(self.gm_in_dwi)
        self.mask = math_img('img > 0', img=self.t_img)
        self.mask.to_filename(self.gm_in_dwi_bin)

        # Erode and mask CSF with ventricle mask and and subtract atlas
        print('Masking CSF with ventricle mask...')
        cmd='fslmaths ' + self.vent_mask_dwi + ' -bin ' + self.vent_mask_dwi
        os.system(cmd)
	cmd='fslmaths ' + self.wm_in_dwi_bin + ' -binv ' + self.wm_in_dwi_binv
        os.system(cmd)
        cmd='fslmaths ' + self.gm_in_dwi_bin + ' -binv ' + self.gm_in_dwi_binv
        os.system(cmd)
        cmd='fslmaths ' + self.csf_mask_dwi + ' -mas ' + self.vent_mask_dwi + ' -mas ' + self.wm_in_dwi_binv + ' -mas ' + self.gm_in_dwi_binv + ' ' + self.vent_csf_in_dwi
        os.system(cmd)
        cmd='fslmaths ' + self.vent_csf_in_dwi + ' -bin ' + self.vent_csf_in_dwi_bin
        os.system(cmd)

	# Create gm-wm interface image
        cmd = 'fslmaths ' + self.gm_in_dwi + ' -mul ' + self.wm_in_dwi + ' -bin ' + self.wm_gm_int_in_dwi
        os.system(cmd)

        return


class epi_register(object):
    def __init__(self, epi, t1w, t1w_brain, atlas, atlas_brain, atlas_mask,
                 aligned_epi, aligned_t1w, namer):
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
            namer:
                - naming utility.
        """
        super(register, self).__init__()

        # for naming temporary files
        self.epi_name = mgu.get_filename(epi)
        self.t1w_name = "{}_T1w".format(namer.__suball__)
        self.atlas_name = mgu.get_filename(atlas)
        self.namer = namer
        self.outdir = namer.dirs['tmp']

        # our basic dependencies
        self.epi = epi
        self.t1w = t1w
        self.t1w_brain = t1w_brain
        self.atlas = atlas
        self.atlas_brain = atlas_brain
        self.atlas_mask = atlas_mask
        self.taligned_epi = aligned_epi
        self.taligned_t1w = aligned_t1w
        t1w_skull = "{}/{}_temp-aligned_skull.nii.gz"
        self.taligned_t1w_skull = t1w_skull.format(self.outdir['reg_a'],
                                                   self.t1w_name)
        # strategies for qa later
        self.sreg_strat = None
        self.treg_strat = None

        # if we do bbr, then we will need a wm mask, so store for qa
        self.wm_mask = None

        if sum(nib.load(t1w).header.get_zooms()) <= 6:
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
        mgru.align(self.epi, self.t1w_brain, xfm=xfm_init1, bins=None,
                   dof=None, cost=None, searchrad=None,
                   sch="${FSLDIR}/etc/flirtsch/sch3Dtrans_3dof")
        # perform a near local-only registration, which looks for local
        # fits of the voxels and will improve our registration if our
        # image is for instance cut off somewhere with simple3d
        # make sure to initialize with our translationally optimal fit
        mgru.align(self.epi, self.t1w_brain, xfm=xfm_init2, init=xfm_init1,
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
            mgru.align(self.epi, self.t1w_brain, xfm=xfm_init3,
                       init=xfm_init2, bins=None, dof=6, cost=None,
                       searchrad=None, sch=None)
            # segment the t1w brain into probability maps
            map_path = "{}/{}_seg".format(self.outdir['reg_a'],
                                          self.t1w_name)
            maps = mgnu.segment_t1w(self.t1w_brain, map_path)
            wm_mask = "{}/{}_wmm.nii.gz".format(self.outdir['reg_a'],
                                                self.t1w_name)
            self.wm_mask = wm_mask
            # use the probability maps to extract white matter mask
            mgnu.probmap2mask(maps['wm_prob'], wm_mask, 0.5)
            # perform flirt with boundary-based registration, using the
            # white matter mask to improve registration quality
            mgru.align(self.epi, self.t1w, xfm=xfm_bbr, wmseg=wm_mask,
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
            print("Warning: BBR self registration not "
                  "attempted, as input is low quality.")
            # use the 3d image and transform from the near-local registration
            # instead
            self.sreg_xfm = xfm_init2
            self.sreg_brain = epi_init
            self.sreg_strat = 'flirt'
        # have to use bet for this, as afni 3dautomask
        # only works on 4d volumes
        mgru.extract_brain(self.sreg_brain, self.sreg_brain,
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
        mgru.align(self.t1w_brain, self.atlas_brain, xfm=xfm_t1w2temp_init,
                   init=None, bins=None, dof=None, cost=None, searchrad=None,
                   out=None, sch="${FSLDIR}/etc/flirtsch/sch3Dtrans_3dof")

        # linear registration from t1 space to atlas space with a 12 dof
        # linear registration to serve as our initializer
        mgru.align(self.t1w_brain, self.atlas_brain, xfm=xfm_t1w2temp,
                   out=None, dof=12, searchrad=True, bins=256, interp="spline",
                   wmseg=None, init=xfm_t1w2temp_init)

        self.epi_aligned_skull = "{}/{}_temp-aligned_skull.nii.gz".format(
            self.outdir['reg_m'],
            self.epi_name
        )  # template-aligned with skull
        # if the atlas is MNI 2mm, then we have a config file for it
        if (nib.load(self.atlas).get_data().shape in [(91, 109, 91)] and
                (self.simple is False)):
            warp_t1w2temp = "{}/{}_warp_t1w2temp.nii.gz".format(
                self.outdir['reg_a'],
                self.epi_name
            )  # to store the template warp
            # use FNIRT to nonlinearly align from the t1w to the
            # template space, using the 12 dof transform as an initializer
            mgru.align_nonlinear(self.t1w, self.atlas, xfm_t1w2temp,
                                 warp_t1w2temp, mask=self.atlas_mask)
            # apply the warp from the epi to the atlas space by first using
            # the linear transform from the epi to the template space
            mgru.apply_warp(self.epi, self.atlas, self.epi_aligned_skull,
                            warp=warp_t1w2temp, xfm=self.sreg_xfm)
            # apply the warp from the t1w to the atlas space
            mgru.apply_warp(self.t1w, self.atlas, self.taligned_t1w_skull,
                            warp=warp_t1w2temp)
            self.treg_strat = 'fnirt'  # strategy details
        else:
            # if we dont have 2mm mni or a low quality t1w, FNIRT is unsuitable
            print
            "Atlas is not 2mm MNI, or input is low quality."
            print
            "Using linear template registration."

            xfm_epi2temp = "{}/{}_xfm_epi2temp.mat".format(
                self.outdir['reg_m'],
                self.epi_name
            )
            # just combine our 12 dof linear transform from t1w to template
            # with our transform from epi to t1w space to get a transform
            # from epi ->(-> t1w ->)-> temp space (epi -> temp)
            mgru.combine_xfms(xfm_t1w2temp, self.sreg_xfm, xfm_epi2temp)
            # apply linear transformation from epi to template space
            mgru.applyxfm(self.epi, self.atlas, xfm_epi2temp,
                          self.epi_aligned_skull, interp='spline')
            # apply 12 dof linear transform from t1w to template space
            mgru.apply_warp(self.t1w, self.atlas, self.taligned_t1w_skull,
                            xfm=xfm_t1w2temp)
            self.treg_strat = 'flirt'  # strategy
        # use BET to extract brain from our epi volume
        mgru.extract_brain(self.epi_aligned_skull, self.taligned_epi,
                           opts='-F')

        # use AFNI to extract brain from our t1w volume
        mgru.extract_t1w_brain(self.taligned_t1w_skull, self.taligned_t1w,
                               self.outdir['reg_a'])
        pass
