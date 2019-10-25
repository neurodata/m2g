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


import warnings

warnings.simplefilter("ignore")
import numpy as np
import nibabel as nib
from dipy.tracking.streamline import Streamlines


def build_seed_list(mask_img_file, stream_affine, dens):
    """uses dipy tractography utilities in order to create a seed list for tractography
    
    Parameters
    ----------
    mask_img_file : str
        path to mask of area to generate seeds for
    stream_affine : ndarray
        4x4 array with 1s diagonally and 0s everywhere else
    dens : int
        seed density
    
    Returns
    -------
    ndarray
        locations for the seeds
    """
    from dipy.tracking import utils

    mask_img = nib.load(mask_img_file)
    mask_img_data = mask_img.get_data().astype("bool")
    seeds = utils.random_seeds_from_mask(
        mask_img_data,
        seeds_count=int(dens),
        seed_count_per_voxel=True,
        affine=stream_affine,
    )
    return seeds


def tens_mod_fa_est(gtab, dwi_file, B0_mask):
    """Estimate a tensor FA image to use for registrations using dipy functions
    
    Parameters
    ----------
    gtab : GradientTable
        gradient table created from bval and bvec file
    dwi_file : str
        Path to eddy-corrected and RAS reoriented dwi image
    B0_mask : str
        Path to nodif B0 mask (averaged b0 mask)
    
    Returns
    -------
    str
        Path to tensor_fa image file
    """
    import os
    from dipy.reconst.dti import TensorModel
    from dipy.reconst.dti import fractional_anisotropy

    data = nib.load(dwi_file).get_fdata()

    print("Generating simple tensor FA image to use for registrations...")
    nodif_B0_img = nib.load(B0_mask)
    B0_mask_data = nodif_B0_img.get_fdata().astype("bool")
    nodif_B0_affine = nodif_B0_img.affine
    model = TensorModel(gtab)
    mod = model.fit(data, B0_mask_data)
    FA = fractional_anisotropy(mod.evals)
    FA[np.isnan(FA)] = 0
    fa_img = nib.Nifti1Image(FA.astype(np.float32), nodif_B0_affine)
    fa_path = "%s%s" % (os.path.dirname(B0_mask), "/tensor_fa.nii.gz")
    nib.save(fa_img, fa_path)
    return fa_path


class run_track(object):
    def __init__(
        self,
        dwi_in,
        nodif_B0_mask,
        gm_in_dwi,
        vent_csf_in_dwi,
        csf_in_dwi,
        wm_in_dwi,
        gtab,
        mod_type,
        track_type,
        mod_func,
        seeds,
        stream_affine,
    ):
        """A class for deterministic tractography in native space
        
        Parameters
        ----------
        dwi_in : str
            path to the input dwi image to perform tractography on.
            Should be a nifti, gzipped nifti, or other image that nibabel
            is capable of reading, with data as a 4D object.
        nodif_B0_mask : str
            path to the mask of the b0 mean volume. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        gm_in_dwi : str
            Path to gray matter segmentation in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object
        vent_csf_in_dwi : str
            Ventricular CSF Mask in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object
        csf_in_dwi : str
            Path to CSF mask in EPI space. Should be a nifti, gzipped nifti, or other image file that nibabel compatable
        wm_in_dwi : str
            Path to white matter probabilities in EPI space. Should be a nifti,
            gzipped nifti, or other image file that nibabel is capable of
            reading, with data as a 3D object.
        gtab : gradient table
            gradient table created from bval and bvec files
        mod_type : str
            Determinstic (det) or probabilistic (prob) tracking
        track_type : str
            Tracking approach: local or particle
        mod_func : str
            Diffusion model: csd or csa
        seeds : ndarray
            ndarray of seeds for tractography
        stream_affine : ndarray
            4x4 2D array with 1s diagonaly and 0s everywhere else
        """
        
        self.dwi = dwi_in
        self.nodif_B0_mask = nodif_B0_mask
        self.gm_in_dwi = gm_in_dwi
        self.vent_csf_in_dwi = vent_csf_in_dwi
        self.csf_in_dwi = csf_in_dwi
        self.wm_in_dwi = wm_in_dwi
        self.gtab = gtab
        self.mod_type = mod_type
        self.track_type = track_type
        self.seeds = seeds
        self.mod_func = mod_func
        self.stream_affine = stream_affine

    def run(self):
        """Creates the tracktography tracks using dipy commands and the specified tracking type and approach
        
        Returns
        -------
        ArraySequence
            contains the tractography track raw data for further analysis
        
        Raises
        ------
        ValueError
            Raised when no seeds are supplied or no valid seeds were found in white-matter interface
        ValueError
            Raised when no seeds are supplied or no valid seeds were found in white-matter interface
        """
        self.tiss_classifier = self.prep_tracking()
        if self.mod_type == "det":
            if self.mod_func == "csa":
                self.mod = self.odf_mod_est()
            elif self.mod_func == "csd":
                self.mod = self.csd_mod_est()
            if self.track_type == "local":
                tracks = self.local_tracking()
            elif self.track_type == "particle":
                tracks = self.particle_tracking()
            else:
                raise ValueError(
                    "Error: Either no seeds supplied, or no valid seeds found in white-matter interface"
                )
        elif self.mod_type == "prob":
            if self.mod_func == "csa":
                self.mod = self.odf_mod_est()
            elif self.mod_func == "csd":
                self.mod = self.csd_mod_est()
            if self.track_type == "local":
                tracks = self.local_tracking()
            elif self.track_type == "particle":
                tracks = self.particle_tracking()
        else:
            raise ValueError(
                "Error: Either no seeds supplied, or no valid seeds found in white-matter interface"
            )
        return tracks

    def prep_tracking(self):
        """Uses nibabel and dipy functions in order to load the grey matter, white matter, and csf masks
        and use a tissue classifier (act, cmc, or binary) on the include/exclude maps to make a tissueclassifier object
        
        Returns
        -------
        ActTissueClassifier, CmcTissueClassifier, or BinaryTissueCLassifier
            The resulting tissue classifier object, depending on which method you use (currently only does act)
        """
        from dipy.tracking.local import (
            ActTissueClassifier,
            CmcTissueClassifier,
            BinaryTissueClassifier,
        )  # TODO: these classes no longer exist in dipy 1.0.

        if self.track_type == "local":
            tiss_class = "bin"
        elif self.track_type == "particle":
            tiss_class = "cmc"

        self.dwi_img = nib.load(self.dwi)
        self.data = self.dwi_img.get_data()
        # Loads mask and ensures it's a true binary mask
        self.mask_img = nib.load(self.nodif_B0_mask)
        self.mask = self.mask_img.get_data() > 0
        # Load tissue maps and prepare tissue classifier
        self.gm_mask = nib.load(self.gm_in_dwi)
        self.gm_mask_data = self.gm_mask.get_data()
        self.wm_mask = nib.load(self.wm_in_dwi)
        self.wm_mask_data = self.wm_mask.get_data()
        self.wm_in_dwi_data = nib.load(self.wm_in_dwi).get_data().astype("bool")
        if tiss_class == "act":
            self.vent_csf_in_dwi = nib.load(self.vent_csf_in_dwi)
            self.vent_csf_in_dwi_data = self.vent_csf_in_dwi.get_data()
            self.background = np.ones(self.gm_mask.shape)
            self.background[
                (self.gm_mask_data + self.wm_mask_data + self.vent_csf_in_dwi_data) > 0
            ] = 0
            self.include_map = self.wm_mask_data
            self.include_map[self.background > 0] = 0
            self.exclude_map = self.vent_csf_in_dwi_data
            self.tiss_classifier = ActTissueClassifier(
                self.include_map, self.exclude_map
            )
        elif tiss_class == "bin":
            self.tiss_classifier = BinaryTissueClassifier(self.wm_in_dwi_data)
            # self.tiss_classifier = BinaryTissueClassifier(self.mask)
        elif tiss_class == "cmc":
            self.vent_csf_in_dwi = nib.load(self.vent_csf_in_dwi)
            self.vent_csf_in_dwi_data = self.vent_csf_in_dwi.get_data()
            voxel_size = np.average(self.wm_mask.get_header()["pixdim"][1:4])
            step_size = 0.2
            self.tiss_classifier = CmcTissueClassifier.from_pve(
                self.wm_mask_data,
                self.gm_mask_data,
                self.vent_csf_in_dwi_data,
                step_size=step_size,
                average_voxel_size=voxel_size,
            )
        else:
            pass
        return self.tiss_classifier

    def tens_mod_est(self):
        from dipy.reconst.dti import TensorModel, quantize_evecs
        from dipy.data import get_sphere

        print("Fitting tensor model...")
        self.model = TensorModel(self.gtab)
        self.ten = self.model.fit(self.data, self.wm_in_dwi_data)
        self.fa = self.ten.fa
        self.fa[np.isnan(self.fa)] = 0
        self.sphere = get_sphere("repulsion724")
        self.ind = quantize_evecs(self.ten.evecs, self.sphere.vertices)
        return self.ten

    def odf_mod_est(self):
        from dipy.reconst.shm import CsaOdfModel

        print("Fitting CSA ODF model...")
        self.mod = CsaOdfModel(self.gtab, sh_order=6)
        return self.mod

    def csd_mod_est(self):
        from dipy.reconst.csdeconv import (
            ConstrainedSphericalDeconvModel,
            recursive_response,
        )

        print("Fitting CSD model...")
        try:
            print("Attempting to use spherical harmonic basis first...")
            self.mod = ConstrainedSphericalDeconvModel(self.gtab, None, sh_order=6)
        except:
            print("Falling back to estimating recursive response...")
            self.response = recursive_response(
                self.gtab,
                self.data,
                mask=self.wm_in_dwi_data,
                sh_order=6,
                peak_thr=0.01,
                init_fa=0.08,
                init_trace=0.0021,
                iter=8,
                convergence=0.001,
                parallel=False,
            )
            print("CSD Reponse: " + str(self.response))
            self.mod = ConstrainedSphericalDeconvModel(self.gtab, self.response)
        return self.mod

    def local_tracking(self):
        from dipy.tracking.local import LocalTracking
        from dipy.data import get_sphere
        from dipy.direction import peaks_from_model, ProbabilisticDirectionGetter

        self.sphere = get_sphere("repulsion724")
        if self.mod_type == "det":
            print("Obtaining peaks from model...")
            self.mod_peaks = peaks_from_model(
                self.mod,  # AttributeError: 'run_track' object has no attribute 'mod' -- should this be mod_func?
                self.data,
                self.sphere,
                relative_peak_threshold=0.5,
                min_separation_angle=25,
                mask=self.wm_in_dwi_data,
                npeaks=5,
                normalize_peaks=True,
            )
            self.streamline_generator = LocalTracking(
                self.mod_peaks,
                self.tiss_classifier,
                self.seeds,
                self.stream_affine,
                step_size=0.5,
                return_all=True,
            )
        elif self.mod_type == "prob":
            print("Preparing probabilistic tracking...")
            print("Fitting model to data...")
            self.mod_fit = self.mod.fit(self.data, self.wm_in_dwi_data)
            print("Building direction-getter...")
            try:
                print(
                    "Proceeding using spherical harmonic coefficient from model estimation..."
                )
                self.pdg = ProbabilisticDirectionGetter.from_shcoeff(
                    self.mod_fit.shm_coeff, max_angle=60.0, sphere=self.sphere
                )
            except:
                print("Proceeding using FOD PMF from model estimation...")
                self.fod = self.mod_fit.odf(self.sphere)
                self.pmf = self.fod.clip(min=0)
                self.pdg = ProbabilisticDirectionGetter.from_pmf(
                    self.pmf, max_angle=60.0, sphere=self.sphere
                )
            self.streamline_generator = LocalTracking(
                self.pdg,
                self.tiss_classifier,
                self.seeds,
                self.stream_affine,
                step_size=0.5,
                return_all=True,
            )
        print("Reconstructing tractogram streamlines...")
        self.streamlines = Streamlines(self.streamline_generator)
        return self.streamlines

    def particle_tracking(self):
        from dipy.tracking.local import ParticleFilteringTracking
        from dipy.data import get_sphere
        from dipy.direction import peaks_from_model, ProbabilisticDirectionGetter

        self.sphere = get_sphere("repulsion724")
        if self.mod_type == "det":
            maxcrossing = 1
            print("Obtaining peaks from model...")
            self.mod_peaks = peaks_from_model(
                self.mod,
                self.data,
                self.sphere,
                relative_peak_threshold=0.5,
                min_separation_angle=25,
                mask=self.wm_in_dwi_data,
                npeaks=5,
                normalize_peaks=True,
            )
            self.streamline_generator = ParticleFilteringTracking(
                self.mod_peaks,
                self.tiss_classifier,
                self.seeds,
                self.stream_affine,
                max_cross=maxcrossing,
                step_size=0.5,
                maxlen=1000,
                pft_back_tracking_dist=2,
                pft_front_tracking_dist=1,
                particle_count=15,
                return_all=True,
            )
        elif self.mod_type == "prob":
            maxcrossing = 2
            print("Preparing probabilistic tracking...")
            print("Fitting model to data...")
            self.mod_fit = self.mod.fit(self.data, self.wm_in_dwi_data)
            print("Building direction-getter...")
            try:
                print(
                    "Proceeding using spherical harmonic coefficient from model estimation..."
                )
                self.pdg = ProbabilisticDirectionGetter.from_shcoeff(
                    self.mod_fit.shm_coeff, max_angle=60.0, sphere=self.sphere
                )
            except:
                print("Proceeding using FOD PMF from model estimation...")
                self.fod = self.mod_fit.odf(self.sphere)
                self.pmf = self.fod.clip(min=0)
                self.pdg = ProbabilisticDirectionGetter.from_pmf(
                    self.pmf, max_angle=60.0, sphere=self.sphere
                )
            self.streamline_generator = ParticleFilteringTracking(
                self.pdg,
                self.tiss_classifier,
                self.seeds,
                self.stream_affine,
                max_cross=maxcrossing,
                step_size=0.5,
                maxlen=1000,
                pft_back_tracking_dist=2,
                pft_front_tracking_dist=1,
                particle_count=15,
                return_all=True,
            )
        print("Reconstructing tractogram streamlines...")
        self.streamlines = Streamlines(self.streamline_generator)
        return self.streamlines


def eudx_basic(dwi_file, gtab, stop_val=0.1):
    import os
    from dipy.reconst.dti import TensorModel, quantize_evecs
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
    mask_out_file = os.path.dirname(dwi_file) + "/dwi_bin_mask.nii.gz"
    nib.save(mask_img, mask_out_file)

    # use all points in mask
    seedIdx = np.where(mask_data > 0)  # seed everywhere not equal to zero
    seedIdx = np.transpose(seedIdx)

    model = TensorModel(gtab)

    # print('data: {}'.format(data))
    print("data shape: {}".format(data.shape))
    print("data type: {}".format(type(data)))
    # print('mask data: {}'.format(mask_data))
    print("mask data shape: {}".format(mask_data.shape))
    print("mask data type: {}".format(type(mask_data)))

    print("data location: {}".format(dwi_file))
    print("mask location: {}".format(mask_out_file))
    ten = model.fit(data, mask_data)
    sphere = get_sphere("symmetric724")
    ind = quantize_evecs(ten.evecs, sphere.vertices)
    streamlines = EuDX(
        a=ten.fa, ind=ind, seeds=seedIdx, odf_vertices=sphere.vertices, a_low=stop_val
    )
    return ten, streamlines, mask_out_file