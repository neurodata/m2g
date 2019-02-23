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
# Created by derek Pisner on 02/17/2019.
# Email: dpisner@utexas.edu

from __future__ import print_function
import warnings
warnings.simplefilter("ignore")
import numpy as np
import nibabel as nib
from dipy.tracking.streamline import Streamlines


def build_seed_list(mask_img_file, stream_affine, dens):
    from dipy.tracking import utils
    mask_img = nib.load(mask_img_file)
    mask_img_data = mask_img.get_data().astype('bool')
    seeds = utils.seeds_from_mask(mask_img_data, density=int(dens), affine=stream_affine)
    return seeds

class run_track(object):
    def __init__(self, dwi_in, nodif_B0_mask, gm_in_dwi, vent_csf_in_dwi, vent_csf_in_dwi_bin,
                 wm_in_dwi, wm_in_dwi_bin, gtab, mod_type, track_type, mod_func, seeds, stream_affine):
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
	self.vent_csf_in_dwi_bin = vent_csf_in_dwi_bin
        self.wm_in_dwi = wm_in_dwi
        self.wm_in_dwi_bin = wm_in_dwi_bin
        self.gtab = gtab
	self.mod_type = mod_type
	self.track_type = track_type
	self.seeds = seeds
	self.mod_func = mod_func
	self.stream_affine = stream_affine

    def run(self):
	self.tiss_classifier = self.prep_tracking()
	if self.mod_type == 'det':
	    if self.track_type == 'eudx':
                self.tens = self.tens_mod_est()
                tracks = self.eudx_tracking()
	    elif self.track_type == 'local':
		if self.mod_func == 'csa':
		    self.mod = self.odf_mod_est()
		elif self.mod_func == 'csd':
		    self.mod = self.csd_mod_est()
		tracks = self.local_tracking()
	    else:
		raise ValueError('Error: Either no seeds supplied, or no valid seeds found in white-matter interface')
	elif self.mod_type == 'prob':
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
	if tiss_class == 'act':
            self.background = np.ones(self.gm_mask.shape)
            self.background[(self.gm_mask_data + self.wm_mask_data + self.vent_csf_mask_data) > 0] = 0
            self.include_map = self.gm_mask.get_data()
            self.include_map[self.background > 0] = 1
            self.exclude_map = self.vent_csf_mask_data
	    self.tiss_classifier = ActTissueClassifier(self.include_map, self.exclude_map)
	elif tiss_class == 'bin':
	    cmd='fslmaths ' + self.wm_in_dwi_bin + ' -sub ' + vent_csf_in_dwi_bin + ' ' + self.wm_in_dwi_bin
 	    os.system(cmd)
	    self.wm_in_dwi_bin_data = nib.load(self.wm_in_dwi_bin).get_data().astype('bool')
	    self.tiss_classifier = BinaryTissueClassifier(self.wm_in_dwi_bin_data)
	else:
	    pass
	return self.tiss_classifier

    def tens_mod_est(self):
	from dipy.reconst.dti import TensorModel, fractional_anisotropy, quantize_evecs
	from dipy.data import get_sphere
        print('Fitting tensor model...')
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
        self.mask = self.mask_img.get_data().astype('bool')
	print('Fitting CSA ODF model...')
	self.mod = CsaOdfModel(self.gtab, sh_order=6)
	return self.mod

    def csd_mod_est(self):
	from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel, recursive_response
	print('Fitting CSD model...')
	try:
	    print('Attempting to use spherical harmonic basis first...')
	    self.mod = ConstrainedSphericalDeconvModel(self.gtab, None, sh_order=6)
	except:
	    print('Falling back to estimating recursive response...')
            self.response = recursive_response(self.gtab, self.data, mask=self.mask, sh_order=8, peak_thr=0.01, init_fa=0.08, init_trace=0.0021, iter=8, convergence=0.001, parallel=False)
	    print('CSD Reponse: ' + str(self.response))
	    self.mod = ConstrainedSphericalDeconvModel(self.gtab, self.response)
	return self.mod

    def local_tracking(self):
	from dipy.tracking.local import LocalTracking
	from dipy.data import default_sphere
	from dipy.direction import peaks_from_model, ProbabilisticDirectionGetter
	if self.mod_type=='det':
	    print('Obtaining peaks from model...')
	    self.mod_peaks = peaks_from_model(self.mod, self.data, default_sphere, relative_peak_threshold=.8, min_separation_angle=45, mask=self.mask)
            self.streamline_generator = LocalTracking(self.mod_peaks, self.tiss_classifier, self.seeds, self.stream_affine, step_size=.5, return_all=True)
        elif self.mod_type=='prob':
	    print('Preparing probabilistic tracking...')
	    print('Fitting model to data...')
	    self.mod_fit = self.mod.fit(self.data, self.mask)
	    print('Building direction-getter...')
	    try:
		print('Proceeding using spherical harmonic coefficient from model estimation...')
                self.pdg = ProbabilisticDirectionGetter.from_shcoeff(self.mod_fit.shm_coeff, max_angle=30., sphere=default_sphere)
	    except:
		print('Proceeding using FOD PMF from model estimation...')
		self.fod = self.mod_fit.odf(default_sphere)
		self.pmf = self.fod.clip(min=0)
		self.pdg = ProbabilisticDirectionGetter.from_pmf(self.pmf, max_angle=30., sphere=default_sphere)
            self.streamline_generator = LocalTracking(self.pdg, self.tiss_classifier, self.seeds, self.stream_affine, step_size=.5, return_all=True)
	print('Reconstructing tractogram streamlines...')
	self.streamlines = Streamlines(self.streamline_generator)
	return self.streamlines

    def eudx_tracking(self):
	from dipy.tracking.eudx import EuDX
        print('Running EuDX tracking...')
        self.streamline_generator = EuDX(self.fa.astype('f8'), self.ind, odf_vertices=self.sphere.vertices, a_low=float(0.2), seeds=self.seeds, affine=self.stream_affine)
        self.streamlines = Streamlines(self.streamline_generator)
        return self.streamlines

def eudx_basic(dwi_file, gtab, stop_val=0.1):
    import os
    from dipy.reconst.dti import TensorModel, fractional_anisotropy, quantize_evecs
    from dipy.tracking.eudx import EuDX
    from dipy.data import get_sphere
    from dipy.segment.mask import median_otsu
    """
    Tracking with basic tensors and basic eudx - experimental
    We now force seeding at every voxel in the provided mask for
    simplicity.  Future functionality will extend these options.
    **Positional Arguments:**
            dwi_file:
                - File (registered) to use for tensor/fiber tracking
            mask:
                - Brain mask to keep tensors inside the brain
            gtab:
                - dipy formatted bval/bvec Structure
    **Optional Arguments:**
            stop_val:
                - Value to cutoff fiber track
    """

    img = nib.load(dwi_file)
    data = img.get_data()

    data_sqz = np.squeeze(data)
    b0_mask, mask_data = median_otsu(data_sqz, 2, 1)
    mask_img = nib.Nifti1Image(mask_data.astype(np.float32), img.affine)
    mask_out_file = os.path.dirname(dwi_file) + '/dwi_bin_mask.nii.gz'
    nib.save(mask_img, mask_out_file)

    # use all points in mask
    seedIdx = np.where(mask_data > 0)  # seed everywhere not equal to zero
    seedIdx = np.transpose(seedIdx)

    model = TensorModel(gtab)
    ten = model.fit(data, mask_data)
    sphere = get_sphere('symmetric724')
    ind = quantize_evecs(ten.evecs, sphere.vertices)
    streamlines = EuDX(a=ten.fa, ind=ind, seeds=seedIdx,
              odf_vertices=sphere.vertices, a_low=stop_val)
    return (ten, streamlines, mask_out_file)
