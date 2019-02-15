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
# Created by derek Pisner on 10/20/2018.
# Email: wgr@jhu.edu

from __future__ import print_function
import warnings
warnings.simplefilter("ignore")
import numpy as np
import nibabel as nib
from dipy.tracking.streamline import Streamlines


def build_seed_list(wm_gm_int_in_dwi):
    from dipy.tracking import utils
    wm_gm_mask = nib.load(wm_gm_int_in_dwi)
    wm_gm_mask_data = wm_gm_mask.get_data().astype('bool')
    seeds = utils.seeds_from_mask(wm_gm_mask_data, density=5, affine=wm_gm_mask.affine)
    return seeds

class run_track(object):
    def __init__(self, dwi_in, nodif_B0_mask, gm_in_dwi, vent_csf_in_dwi,
                 wm_in_dwi, wm_in_dwi_bin, gtab, mod_type, track_type, mod_func, seeds):
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
        gtab: string
            - Gradient table.
        """
        self.dwi = dwi_in
        self.nodif_B0_mask = nodif_B0_mask
        self.gm_in_dwi = gm_in_dwi
        self.vent_csf_in_dwi = vent_csf_in_dwi
        self.wm_in_dwi = wm_in_dwi
        self.wm_in_dwi_bin = wm_in_dwi_bin
        self.gtab = gtab
	self.mod_type = mod_type
	self.track_type = track_type
	self.seeds = seeds
	self.mod_func = mod_func

    def run(self):
	if self.track_type == 'local':
	    self.tiss_classifier = self.prep_tracking()
	if self.mod_type == 'det':
	    if self.track_type == 'eudx':
                self.tens = self.tens_mod_est()
                tracks = self.eudx_tracking()
	    elif self.track_type == 'local':
		if self.seeds is not None and len(self.seeds) > 0:
		    if self.mod_func == 'csa':
		    	self.mod = self.odf_mod_est()
		    elif self.mod_func == 'csd':
			self.mod = self.csd_mod_est()
		    tracks = self.local_tracking()
		else:
		    raise ValueError('Error: Either no seeds supplied, or no valid seeds found in white-matter interface')
	elif self.mod_type == 'prob':
            if self.seeds is not None and len(self.seeds) > 0:
                if self.mod_func == 'csa':
                    self.mod = self.odf_mod_est()
                elif self.mod_func == 'csd':
                    self.mod = self.csd_mod_est()
                tracks = self.local_tracking()
            else:
                raise ValueError('Error: Either no seeds supplied, or no valid seeds found in white-matter interface')
        return tracks

    def prep_tracking(self):
	from dipy.tracking.local import ActTissueClassifier
	from dipy.tracking.local import BinaryTissueClassifier
	tiss_class = 'bin'
	if tiss_class == 'act':
            self.dwi_img = nib.load(self.dwi)
            self.data = self.dwi_img.get_data()
            # Loads mask and ensures it's a true binary mask
            self.mask_img = nib.load(self.nodif_B0_mask)
            self.mask = self.mask_img.get_data() > 0
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
	    self.tiss_classifier = ActTissueClassifier(self.include_map, self.exclude_map)
	elif tiss_class == 'bin':
	    self.tiss_classifier = BinaryTissueClassifier(self.mask)
	return self.tiss_classifier

    def tens_mod_est(self):
	from dipy.reconst.dti import TensorModel, fractional_anisotropy, quantize_evecs
	from dipy.data import get_sphere
        print('Fitting tensor model...')
        self.dwi_img = nib.load(self.dwi)
        self.data = self.dwi_img.get_data()
        self.mask_img = nib.load(self.nodif_B0_mask)
        self.mask = self.mask_img.get_data() > 0
        self.model = TensorModel(self.gtab)
        self.ten = self.model.fit(self.data, self.mask)
        self.fa = self.ten.fa
	self.fa[np.isnan(self.fa)] = 0
        self.sphere = get_sphere('symmetric724')
        self.ind = quantize_evecs(self.ten.evecs, self.sphere.vertices)
        return self.ten

    def odf_mod_est(self):
	from dipy.reconst.shm import CsaOdfModel
	from dipy.data import default_sphere
	self.mask_img = nib.load(self.nodif_B0_mask)
        self.mask = self.mask_img.get_data() > 0
	self.mod = CsaOdfModel(self.gtab, sh_order=6)
	return self.mod

    def csd_mod_est(self):
	from dipy.reconst.csdeconv import auto_response
	from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel, recursive_response
	response, ratio = auto_response(self.gtab, self.data, roi_radius=10, fa_thr=0.7)
	print('CSD Reponse: '+ response)
	print('CSD Ratio: ' + ratio)
        self.response = recursive_response(self.gtab, self.data, mask=self.mask, sh_order=8, peak_thr=0.01, init_fa=0.08, init_trace=0.0021, iter=8, convergence=0.001, parallel=False)
	self.mod = ConstrainedSphericalDeconvModel(self.gtab, self.response)
	return self.mod

    def local_tracking(self):
	from dipy.tracking.local import LocalTracking
	from dipy.data import default_sphere
	from dipy.direction import peaks_from_model, ProbabilisticDirectionGetter
	if self.mod_type=='det':
	    self.mod_peaks = peaks_from_model(self.mod, self.data, default_sphere, normalize_peaks=True, relative_peak_threshold=.8, min_separation_angle=45, mask=self.mask)
            self.streamline_generator = LocalTracking(self.mod_peaks, self.tiss_classifier, self.seeds, self.dwi_img.affine, step_size=.5, return_all=True)
        elif self.mod_type=='prob':
	    try:
                self.pdg = ProbabilisticDirectionGetter.from_shcoeff(self.mod.shm_coeff, max_angle=30., sphere=self.default_sphere)
	    except:
		print('Failed to obtain spherical harmonic from csd estimator. Proceeding using FOD PMF from csd estimation instead...')
		self.fod = self.mod.odf(default_sphere)
		self.pmf = self.fod.clip(min=0)
		self.pdg = ProbabilisticDirectionGetter.from_pmf(self.pmf, max_angle=30., sphere=default_sphere) 
            self.streamline_generator = LocalTracking(self.pdg, self.tiss_classifier, self.seeds, self.dwi_img.affine, step_size=.5, return_all=True)
	self.streamlines = Streamlines(self.streamline_generator, buffer_size=512)
	return self.streamlines

    def eudx_tracking(self):
	from dipy.tracking.eudx import EuDX
        print('Running deterministic tractography...')
        self.streamline_generator = EuDX(self.fa.astype('f8'), self.ind, odf_vertices=self.sphere.vertices, a_low=float(0.02), seeds=int(1000000), affine=self.dwi_img.affine)
        self.streamlines = Streamlines(self.streamline_generator, buffer_size=512)
        return self.streamlines
