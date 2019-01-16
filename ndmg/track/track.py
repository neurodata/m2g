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
# track.py
# Created by Will Gray Roncal on 2016-01-28.
# Email: wgr@jhu.edu

from __future__ import print_function

from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel, recursive_response
from dipy.tracking.local import ActTissueClassifier
from dipy.tracking import streamline
from dipy.direction import ProbabilisticDirectionGetter
from dipy.data import default_sphere
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs


class track(object):
    def __init__(self, dwi_in, nodif_B0_mask, gm_in_dwi, vent_csf_in_dwi,
                 wm_in_dwi, wm_in_dwi_bin, fbval_in, fbvec_in,
                 dwi_aligned_atlas, seeds=1000000, a_low=0.02, step_sz=0.5,
                 max_points=2000, ang_thr=60.0):
        """
        A class for deterministic tractography in native space.

        Parameters
        ----------
        dwi_in: string
            - path to the input dMRI image to perform tractography on.
            Should be a nifti, gzipped nifti, or other image that nibabel
            is capable of reading, with data as a 4D object.
        nodif_B0_mask: string
            - path to the mask of the b0 mean volume. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        gm_in_dwi: string
            - Path to gray matter segmentation in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        vent_csf_in_dwi: string
            - Ventricular CSF Mask in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        wm_in_dwi: string
            - Path to white matter probabilities in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        wm_in_dwi_bin: string
            - Path to a binarized white matter segmentation in EPI space.
            Should be a nifti, gzipped nifti, or other image file that 
            nibabel is capable of reading, with data as a 3D object.
        fbval_in: string
            - Path to the BValue file, as a ssv.
        fbvec_in: string
            - Path to the BVector file, as a ssv.
        seeds: int
            - the number of seeds to use for tractography.
        a_low: float
        step_sz: float
            - Step Size.
        max_points: int
        ang_thr: float
            - Angular Threshold for the angle fibers can take.
        """
        self.dwi = dwi_in
        self.nodif_B0_mask = nodif_B0_mask
        self.gm_in_dwi = gm_in_dwi
        self.vent_csf_in_dwi = vent_csf_in_dwi
        self.wm_in_dwi = wm_in_dwi
        self.wm_in_dwi_bin = wm_in_dwi_bin
        self.fbval = fbval_in
        self.fbvec = fbvec_in
        self.dwi_aligned_atlas = dwi_aligned_atlas

    def run(self):
        self.prep_tracking()
        self.tens_mod_est()
        tracks = self.det_connectometry()
        return tracks

    def prep_tracking(self):

        self.dwi_img = nib.load(self.dwi)
        self.data = self.dwi_img.get_data()

        # Loads mask and ensures it's a true binary mask
        self.mask_img = nib.load(self.nodif_B0_mask)
        self.mask = self.mask_img.get_data() > 0

        # loading bvecs/bvals
        self.bvals, self.bvecs = read_bvals_bvecs(self.fbval, self.fbvec)

        # Creating the gradient table
        self.gtab = gradient_table(self.bvals, self.bvecs)

        # Load tissue maps and prepare tissue classifier
        self.gm_mask = nib.load(self.gm_in_dwi)
        self.gm_mask_data = self.gm_mask.get_data().astype('bool')
        self.vent_csf_mask = nib.load(self.vent_csf_in_dwi)
        self.vent_csf_mask_data = self.vent_csf_mask.get_data().astype('bool')
        self.wm_mask = nib.load(self.wm_in_dwi)
        self.wm_mask_data = self.wm_mask.get_data().astype('bool')
        self.background = np.ones(self.gm_mask.shape)
        self.background[(self.gm_mask_data + self.wm_mask_data + self.vent_csf_mask_data) > 0] = 0
        self.include_map = self.gm_mask.get_data()
        self.include_map[self.background > 0] = 1
        self.exclude_map = self.vent_csf_mask_data

    def tens_mod_est(self):
        print('Fitting tensor model...')
        self.model = TensorModel(self.gtab)
        self.ten = self.model.fit(self.data, self.mask)
        self.fa = self.ten.fa
        self.sphere = get_sphere('symmetric724')
        self.ind = quantize_evecs(self.ten.evecs, self.sphere.vertices)
        return

    def det_connectometry(self):
        print('Running deterministic tractography...')
        self.streamline_generator = EuDX(self.fa, self.ind, odf_vertices=self.sphere.vertices, 
            a_low=self.a_low, seeds=self.seeds, step_sz=self.step_sz,
            max_points=self.max_points, ang_thr=self.ang_thr, affine=self.dwi_img.affine)
        self.streamlines = Streamlines(self.streamline_generator, buffer_size=512)
        self.tracks = [sl for sl in self.streamlines if len(sl) > 1]
        return self.tracks
