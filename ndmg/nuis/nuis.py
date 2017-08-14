#!/usr/bin/env python
#
# Copyright 2016 NeuroData (http://neuromri_dat.io)
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
#
# nuis.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu
from ndmg.utils import utils as mgu
from ndmg.utils import nuis_utils as mgnu
import nibabel as nb
import numpy as np
from scipy.fftpack import rfft, irfft, rfftfreq


class nuis(object):

    def __init__(self, fmri, smri, nuis_mri, outdir, lv_mask,
                 mc_params=None):
        """
        A class for nuisance correction of fMRI.

        **Positional Arguments:**

            - fmri:
                - the functional mri.
            - smri:
                - the structural mri (assumed to be T1w).
            - nuis_mri:
                - the file path of a nuisance corrected mri
            - lv_mask:
                - lateral-ventricles mask.
            - mc_params:
                - the path to a motion parameters file. Should have
                  6 parameters for x/y/z tranlations/rotations per
                  timestep.
        """
        # store our inputs
        self.fmri = fmri  # the fmri
        self.smri = smri  # the T1w anatomical mri
        self.nuis_mri = nuis_mri  # the nuisance-corrected path

        # store the masks so that we can easily do qa later
        self.lv_mask = lv_mask  # lateral-ventricles mask
        self.er_wm_mask = None  # eroded white-matter mask

        # places to place intermediates
        self.outdir = outdir
        self.anat_name = mgu.get_filename(smri)
        # store temporary path for segmentation step
        nuisname = "{}_nuis".format(self.anat_name)
        self.nuisname = nuisname
        # wm mask
        self.wm_mask = "{}/{}_wmm.nii.gz".format(self.outdir, nuisname)
        # csf mask not used due to inconsistencies in segmenting
        # gm mask
        self.gm_mask = "{}/{}_gmm.nii.gz".format(self.outdir, nuisname)
        self.map_path = "{}/{}_seg".format(self.outdir, nuisname)
        # segment the brain for quality control purposes
        maps = mgnu.segment_t1w(self.smri, self.map_path, opts='-P')
        # extract the masks
        self.wm_prob = maps['wm_prob']
        mgnu.probmap2mask(maps['wm_prob'], self.wm_mask, .99)
        mgnu.probmap2mask(maps['gm_prob'], self.gm_mask, .95)
        # the centered brain
        self.cent_nuis = None
        # the brain after glm
        self.glm_nuis = None
        # the brain after frequency correction
        self.fft_nuis = None
        # regressors so that we can use them for line plots
        self.csf_reg = None
        self.wm_reg = None
        self.cc_reg = None
        self.quad_reg = None
        self.fft_reg = None
        self.fft_bef = None
        self.mot_reg = None

        # signal that is removed at given steps
        self.fft_sig = None
        self.glm_sig = None
        self.mc_params_file = mc_params
        pass

    def center_signal(self, data):
        """
        A function that performs normalization to a
        given fMRI signal, non-transposed. We subtract out the mean of
        each dimension.

        **Positional Arguments:**

            data:
                - the fMRI data. Should be passed as an ndarray,
                  with dimensions [xdim, ydim, zdim, ntimesteps].
        """
        print "Centering Signal..."
        data = data - data.mean(axis=3, keepdims=True)
        return data

    def normalize_signal(self, data):
        """
        A function taht performs normalization by the standard deviation
        to a fMRI signal. We divide by the standard deviation of the signal
        so that the voxel timeseries are of relatively equal magnitude,
        as the standard deviation is the primary contrast that we are
        concerned with.

        **Positional Arguments:**

            data:
                - the fMRI data. Should be an array, with dimensions
                  [ntimesteps, nvoxels].
        """
        print "Normalizing Signal by Standard Deviation..."
        # normalize the signal
        data = np.divide(data, data.std(axis=0))
        # returns the normalized signal
        return data

    def compcor(self, masked_ts, n=5):
        """
        A function to extract principal components on
        timeseries of nuisance variables.

        **Positional Arguments:**

            masked_ts:
                - the timeseries over a masked region. We assume
                  that this array is already mean centered per voxel.
                  Dimensions should be [ntimesteps, nvoxels].
           n:
                - the number of components to use.
        """
        print "Extracting Nuisance Components..."
        # singular value decomposition to get the ordered
        # principal components
        U, s, V = np.linalg.svd(masked_ts)
        # return the top n principal components
        return U[:, 0:n], s

    def freq_filter(self, mri, tr, highpass=0.01, lowpass=None):
        """
        A function that uses scipy's fft and ifft to frequency filter
        an fMRI image.

        **Positional Arguments:**
            mri:
                - an ndarray containing timeseries of dimensions
                  [voxels,timesteps] which the user wants to have
                  frequency filtered.
            highpass:
                - the lower limit frequency band to remove below.
            lowpass:
                - the upper limit  frequency band to remove above.
        """
        # apply the fft per voxel to take to fourier domain
        passed_fft = np.apply_along_axis(rfft, 0, mri)

        # get the frequencies returned by the fft that we want
        # to use. note that this function returns us a single-sided
        # set of frequencies
        freq_ra = rfftfreq(mri.shape[0], d=tr)
        self.freq_ra = np.sort(freq_ra)
        order = np.argsort(freq_ra)

        # free for memory purposes
        mri = None

        self.fft_bef = np.square(
            passed_fft[:, self.voxel_gm_mask].mean(axis=1))[order]
        bpra = np.zeros(freq_ra.shape, dtype=bool)
        # figure out which positions we will exclude
        if highpass is not None:
            print "filtering below " + str(highpass) + " Hz..."
            bpra[np.abs(freq_ra) < highpass] = True
        if lowpass is not None:
            print "filtering above " + str(lowpass) + " Hz..."
            bpra[np.abs(freq_ra) > lowpass] = True
        print "Applying Frequency Filtering..."
        filtered_ra = np.logical_not(bpra)
        filtered_fft = passed_fft.copy()
        filtered_fft[filtered_ra, :] = 0
        filt_sig = np.apply_along_axis(irfft, 0,
                                       filtered_fft)
        filtered_fft = None
        self.fft_sig = filt_sig[:, self.voxel_gm_mask].mean(axis=1)
        filt_sig = None

        passed_fft[bpra, :] = 0
        self.fft_reg = np.square(
            passed_fft[:, self.voxel_gm_mask].mean(axis=1))[order]
        # go back to time domain
        return np.apply_along_axis(irfft, 0, passed_fft)

    def regress_signal(self, data, R):
        """
        Regresses data to given regressors.

        **Positional Arguments:**

            data:
                - the data as a ndarray.
            R:
                - a numpy ndarray of regressors to
                  regress to.
        """
        print "GLM with Design Matrix of Dimensions " + str(R.shape) + "..."
        # OLS solution for GLM B = (X^TX)^(-1)X^TY
        coefs = np.linalg.inv(R.T.dot(R)).dot(R.T).dot(data)
        return R.dot(coefs)

    def friston_model(self, mc_params):
        """
        A function that computes the friston 24 parameter
        model for motion regressors. This model can then
        be incorporated into a GLM for correction of motion-related
        nuisance.

        **Positional Arguments:**

            mc_params:
                - a txm matrix of the motion parameters per timepoint,
                  for m regressors.
        """
        (t, m) = mc_params.shape
        friston = np.zeros((t, 4*m))
        # the motion parameters themselves
        friston[:, 0:m] = mc_params
        # square the motion parameters
        friston[:, m:2*m] = np.square(mc_params)

        # use the motion estimated at the preceding timepoint
        # as a regressor
        friston[1:, 2*m:3*m] = mc_params[:-1, :]
        # use the motion estimated at the preceding timepoint
        # squared as a regressor
        friston[:, 3*m:4*m] = np.square(friston[:, 2*m:3*m])
        return friston

    def linear_reg(self, voxel, mc_params, wm_ts=None, csf_ts=None, cc=5,
                   wm_mean=False, csf_mean=False, mot=24, trend='quad'):
        """
        A function to perform quadratic detrending of fMRI data.

        **Positional Arguments**

            voxel:
                - an ndarray containing a voxel timeseries.
                  dimensions should be [timesteps, voxels]
            wm_ts:
                - a timeseries for white matter regression. 
            csf_ts:
                - a timeseries for csf mean regression.
            cc:
                - the number of components for compcor regression.
            wm_mean:
                - whether to perform white-matter mean signal removal.
            csf_mean:
                - whether to remove csf mean signal.
            mot:
                - the number of motion parameters to use.
            trend:
                - the detrend method to use.
        """
        # time dimension is now the 0th dim
        time = voxel.shape[0]
        # linear drift regressor
        lin_reg = np.array(range(0, time))
        # quadratic drift regressor
        quad_reg = np.array(range(0, time))**2

        # use GLM model given regressors to approximate the weight we want
        # to regress out
        R = np.column_stack((np.ones(time))).T
        if trend is not None:
            print "Adding linear trendline to GLM..."
            R = np.column_stack((R, lin_reg))
        if trend == 'quad':
            print "Adding quadratic trendline to GLM..."
            R = np.column_stack((R, quad_reg))


        if csf_mean is not False:
            print "Adding csf mean signal to GLM..."
            csf_reg = csf_ts.mean(axis=1, keepdims=True)
            self.csf_reg = csf_reg  # save for qa later
            # add coefficients to our regression
            R = np.column_stack((R, csf_reg))

        if wm_mean is not False:
            print "Adding wm mean signal to GLM..."
            self.wm_reg = wm_ts.mean(axis=1, keepdims=True)
            R = np.column_stack((R, self.wm_reg))

        if cc is not None and wm_ts is not None and csf_ts is not None:
            print "Adding {} acompcor regressors to GLM...".format(cc)
            self.cc_reg = self.compcor(np.column_stack((csf_ts, wm_ts)),
                                       n=cc)[0]
            R = np.column_stack((R, self.cc_reg))

        if mot == 6 and mc_params is not None:
            print "Adding 6 motion parameters to GLM..."
            self.mot_Reg = mc_params
            R = np.column_stack((R, mc_params))
        elif mot == 24 and mc_params is not None:
            print "Adding 24 Friston parameters to GLM..."
            self.mot_reg = self.friston_model(mc_params)
            R = np.column_stack((R, self.mot_reg))

        WR = self.regress_signal(voxel, R)
        self.glm_sig = WR[:, self.voxel_gm_mask].mean(axis=1)

        # corr'd ts is the difference btwn the original timeseries and
        # our regressors, and then we transpose back
        return (voxel - WR)

    def nuis_correct(self, highpass=.01, lowpass=None, cc=5,
                     csf_mean=False, wm_mean=False, mot=24,
                     trend='quad'):
        """
        Removes Nuisance Signals from brain images, using a combination
        of Frequency filtering, and mean csf/quadratic regression.

        **Positional Arguments:**

            highpass:
                - the highpass cutoff for FFT.
            lowpass:
                - the lowpass cutoff for FFT. NOT recommended.
            cc:
                - the number of components for compcor. If set to None,
                  does not perform compcor.
            csf_mean:
                - whether to use the mean csf signal in the nuisance
                  model.
            wm_mean:
                - whether to use the mean white-matter signal in the nuisance
                  model.
            mot:
                - the number of motion parameters to use for the GLM.
            mc_params_file:
                - the path to a motion parameters space-delimited values file
                  indicating the motion parameters. the .par file associated
                  with mcflirt. If motion regression is specified, this file
                  must be passed.
            trend:
                - whether to remove a linear or quadratic trend from the data.
                  options are 'quad' or 'lin', or None.
        """
        fmri_name = mgu.get_filename(self.fmri)
        fmri_im = nb.load(self.fmri)

        fmri_dat = fmri_im.get_data()
        basic_mask = fmri_dat.sum(axis=3) > 0
        gm_mask_dat = nb.load(self.gm_mask).get_data()
        # mean center signal to start with
        fmri_dat = self.center_signal(fmri_dat)

        # load the voxel timeseries and transpose
        # remove voxels that are absolutely non brain (zero activity)
        # and trim here so that we don't correct for nuis timepoints
        voxel = fmri_dat[basic_mask, :].T

        # zooms are x, y, z, t
        tr = fmri_im.header.get_zooms()[3]

        if cc is not None or csf_mean is not None:
            # load the lateral-ventricles mask which is 0 for excluded,
            # 1 for included
            lvm = nb.load(self.lv_mask).get_data()
            # create t x n array for the n voxels included in the lv mask
            lv_ts = fmri_dat[lvm != 0, :].T
        else:
            lv_ts = None

        # if we are doing something with the white-matter ts,
        # we need to erode our wm mask by 2 voxels to avoid potential
        # signal intensity distortions from adjaceny tissue
        if cc is not None or wm_mean is not False:
            self.er_wm_mask = '{}_{}.nii.gz'.format(self.map_path,
                                                    "wm_mask_eroded")
            # extract the mask where prob map for wm has at least p>.99
            # and erode by 2 voxels
            mgnu.probmap2mask(self.wm_prob, self.er_wm_mask,
                              .99, erode=2)
            # load whitematter mask as binary array of 0 for exclude,
            # 1 for include
            wmm = nb.load(self.er_wm_mask).get_data()
            # wherever the whitematter mask is nonzero, extract the voxels
            # to create t x n array of n voxels in wm mask
            wm_ts = fmri_dat[wmm != 0, :].T
        else:
            wm_ts = None

        # if we have motion parameters, perform motion param regression
        if mot is not None:
            # generate an array that is t x 6 from the mcflirt parameters
            # file by reading column-by-column
            mc_params = np.genfromtxt(self.mc_params_file)
        else:
            mc_params = None

        fmri_dat = None  # free for memory purposes
        self.voxel_gm_mask = gm_mask_dat[basic_mask] > 0
        gm_mask_dat = None  # free for memory
        self.cent_nuis = voxel[:, self.voxel_gm_mask].mean(axis=1)

        # GLM for nuisance correction
        if (cc is not None or csf_mean is not False or wm_mean is not False
            or mot is not None or trend is not None):
            voxel = self.linear_reg(voxel, mc_params, wm_ts=wm_ts, csf_ts=lv_ts,
                                    csf_mean=csf_mean, wm_mean=wm_mean,
                                    mot=mot, trend=trend, cc=cc)
            self.glm_nuis = voxel[:, self.voxel_gm_mask].mean(axis=1)

        # Frequency Filtering for Nuisance Correction
        if highpass is not None or lowpass is not None:
            voxel = self.freq_filter(voxel, tr, highpass=highpass,
                                     lowpass=lowpass)
            self.fft_nuis = voxel[:, self.voxel_gm_mask].mean(axis=1)

        # normalize the signal to account for anatomical
        # intensity differences
        # self.voxel = self.normalize_signal(self.voxel)
        # put the nifti back together again and re-transpose
        fmri_dat = fmri_im.get_data()
        fmri_dat[basic_mask, :] = voxel.T

        # free for memory purposes
        voxel = None
        img = nb.Nifti1Image(fmri_dat,
                             header=fmri_im.header,
                             affine=fmri_im.affine)
        # save the corrected image
        nb.save(img, self.nuis_mri)
        pass
