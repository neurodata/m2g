#!/usr/bin/env python

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

# nuis.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu
from ndmg.utils import utils as mgu
import nibabel as nb
import numpy as np
from ndmg.stats import alignment_qc as mgqc
import scipy.signal as signal
from scipy import fftpack as scifft

class nuis(object):

    def __init__(self):
        """
        A class for nuisance correction of fMRI.
        """
        pass

    def normalize_signal(self, data):
        """
        A function that performs normalization to a
        given fMRI signal. We subtract out the mean of
        each dimension, and then normalze our signal
        by the difference between the maximum and the minimum.

        **Positional Arguments:**
            data:
                - the fMRI data. Should be passed as an ndarray,
                  with dimensions [ntimesteps, nvoxels].
        """
        # remove the voxels that are unchanging, as normalizing
        # these by std would lead to a divide by 0
        data = data[:, data.std(axis=0) != 0]
        data = signal.detrend(data, axis=0, type='linear')
        data = data - data.mean(axis=0)
        # normalize the signal
        data = np.divide(data, data.std(axis=0))
        # returns the normalized signal
        return data

    def compcor(self, masked_ts, n=None, t=None):
        """
        A function to extract principal components on
        timeseries of nuisance variables.

        **Positional Arguments:**
            masked_ts:
                - the timeseries over a masked region.
            n:
                - the number of components to use. Default is None.
                  Note that either n or t should be set, but not
                  both.
            t:
                - the threshold for the amount of expected variance,
                  as a float between 0 and 1, where the number of
                  components returned will be less than the threshold
                  indicated.
        """
        print "Extracting Nuisance Components..."
        # normalize the signal to mean center
        masked_ts = self.normalize_signal(masked_ts)
        # singular value decomposition to get the ordered
        # principal components
        U, s, V = np.linalg.svd(masked_ts)
        if n is not None and t is not None:
            raise ValueError('CompCor: you have passed both a number of \
                              components and a threshold. You should pass \
                              one or the other, not both.')
        elif n is not None:
            # return the top n principal components
            return U[:, 0:n], s
        elif t is not None:
            var_per_comp = s/np.sum(s)  # percent variance of each component
            total_var = np.cumsum(var_per_comp)
            thresh_var = total_var[total_var > t]
            # return up to lowest component greater than threshold
            idx = np.argmin(thresh_var)
            return U[:, 0:idx], s
        else:
            raise ValueError('CompCor: you have not passed a threshold nor \
                              a number of components. You must specify one.')
        pass

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
        fftd = np.apply_along_axis(np.fft.fft, 0, mri)

        # get the frequencies returned by the fft that we want
        # to use. note that this function returns us a single-sided
        # set of frequencies.
        freq_ra = np.fft.fftfreq(mri.shape[0], d=tr)

        bpra = np.zeros(freq_ra.shape, dtype=bool)

        # figure out which positions we will exclude
        if highpass is not None:
            print "filtering below " + str(highpass) + " Hz..."
            bpra[freq_ra < highpass] = True
        if lowpass is not None:
            print "filtering above " + str(lowpass) + " Hz..."
            bpra[freq_ra > lowpass] = True
        print "Applying Frequency Filtering..."
        fftd[bpra, :] = 0
        # go back to time domain
        return np.apply_along_axis(np.fft.ifft, 0, fftd)

    def regress_signal(self, data, R):
        """
        Regresses data to given regressors.

        **Positional Arguments:**
            - data:
                - the data as a ndarray.
            - R:
                - a numpy ndarray of regressors to
                  regress to.
        """
        print "Calculating Regressors..."
        # OLS solution for GLM B = (X^TX)^(-1)X^TY
        coefs = np.linalg.inv(R.T.dot(R)).dot(R.T).dot(data)
        return R.dot(coefs)

    def segment_anat(self, amri, an, basename):
        """
        A function to use FSL's FAST to segment an anatomical
        image into GM, WM, and CSF maps.

        **Positional Arguments:**
            - amri:
                - an anatomical image.
            - an:
                - an integer representing the type of the anatomical image.
                  (1 for T1w, 2 for T2w, 3 for PD).
            - basename:
                - the basename for outputs. Often it will be
                  most convenient for this to be the dataset,
                  followed by the subject, followed by the step of
                  processing. Note that this anticipates a path as well;
                  ie, /path/to/dataset_sub_nuis, with no extension.
        """
        print "Segmenting Anatomical Image into WM, GM, and CSF..."
        # run FAST, with options -t for the image type and -n to
        # segment into CSF (pve_0), WM (pve_1), GM (pve_2)
        cmd = " ".join(["fast -t", str(int(an)), "-n 3 -o", basename, amri])
        mgu().execute_cmd(cmd)
        pass

    def erode_mask(self, mask_path, eroded_path, v=0):
        """
        A function to erode a mask by a specified number of
        voxels. Here, we define erosion as the process of checking
        whether all the voxels within a number of voxels for a
        mask have values.

        **Positional Arguments:**
            - mask_path:
                - a path to a nifti containing a mask.
            - eroded_path:
                - a path to the eroded mask to be created.
            - v:
                - the number of voxels to erode by.
        """
        print "Eroding Mask..."
        mask_img = nb.load(mask_path)
        mask = mask_img.get_data()
        for i in range(0, v):
            # masked_vox is a tuple 0f [x]. [y]. [z] cooords
            # wherever mask is nonzero
            erode_mask = np.zeros(mask.shape)
            x, y, z = np.where(mask != 0)
            if (x.shape == y.shape and y.shape == z.shape):
                # iterated over all the nonzero voxels
                for j in range(0, x.shape[0]):
                    # check that the 3d voxels within 1 voxel are 1
                    # if so, add to the new mask
                    md = mask.shape
                    if (mask[x[j], y[j], z[j]] and
                            mask[np.min((x[j]+1, md[0]-1)), y[j], z[j]] and
                            mask[x[j], np.min((y[j]+1, md[1]-1)), z[j]] and
                            mask[x[j], y[j], np.min((z[j]+1, md[2]-1))] and
                            mask[np.max((x[j]-1, 0)), y[j], z[j]] and
                            mask[x[j], np.max((y[j]-1, 0)), z[j]] and
                            mask[x[j], y[j], np.max((z[j]-1, 0))]):
                        erode_mask[x[j], y[j], z[j]] = 1
            else:
                raise ValueError('Your mask erosion has an invalid shape.')
            mask = erode_mask
        eroded_mask_img = nb.Nifti1Image(mask,
                                         header=mask_img.header,
                                         affine=mask_img.get_affine())
        nb.save(eroded_mask_img, eroded_path)
        return mask

    def extract_mask(self, prob_map, mask_path, t):
        """
        A function to extract a mask from a probability map.
        Also, performs mask erosion as a substep.

        **Positional Arguments:**
            - prob_map:
                - the path to probability map for the given class
                  of brain tissue.
            - mask_path:
                - the path to the extracted mask.
            - t:
                - the threshold to consider voxels part of the class.
        """
        print "Extracting Mask from probability map..."
        prob = nb.load(prob_map)
        prob_dat = prob.get_data()
        mask = (prob_dat > t).astype(int)
        img = nb.Nifti1Image(mask,
                             header=prob.header,
                             affine=prob.get_affine())
        # save the corrected image
        nb.save(img, mask_path)
        return mask

    def linear_reg(self, voxel, csf_reg=None):
        """ 
        A function to perform quadratic detrending of fMRI data.

        **Positional Arguments**
            - voxel:
                - an ndarray containing a voxel timeseries.
                  dimensions should be [timesteps, voxels]
            - csf_reg:
                - a timeseries for csf mean regression. If not
                  provided, regression will not be performed.
        """
        # time dimension is now the 0th dim
        time = voxel.shape[0]
        # linear drift regressor
        lin_reg = np.array(range(0, time))
        # quadratic drift regressor
        quad_reg = np.array(range(0, time))**2

        # use GLM model given regressors to approximate the weight we want
        # to regress out
        R = np.column_stack((np.ones(time), lin_reg, quad_reg))
        if csf_reg is not None:
            # add coefficients to our regression
            np.column_stack((R, csf_reg))

        W = self.regress_signal(voxel, R)
        # corr'd ts is the difference btwn the original timeseries and
        # our regressors, and then we transpose back
        return (voxel - W)

    def nuis_correct(self, fmri, nuisance_mri, er_csfmask=None, highpass=0.01,
                     lowpass=None, qcdir=None):
        """
        Removes Nuisance Signals from brain images, using a combination
        of Frequency filtering, and mean csf/quadratic regression.

        **Positional Arguments:**
            - fmri:
                - the path to a fmri brain as a nifti image.
            - nuisance_fmri:
                - the desired path for the nuisance corrected brain.
            - wmmask:
                - the path to a white matter mask (should be eroded ahead of
                  time).
            - er_csfmask:
                - the path to a lateral ventricles csf mask.
            - highpass:
                - the highpass cutoff for FFT.
            - lowpass:
                - the lowpass cutoff for FFT. NOT recommended.
            - qcdir:
                - the quality control directory to place qc.
        """
        fmri_name = mgu().get_filename(fmri)
        fmri_im = nb.load(fmri)

        fmri_dat = fmri_im.get_data()
        basic_mask = fmri_dat.sum(axis=3) > 0
        # load the voxel timeseries and transpose
        # remove voxels that are absolutely non brain (zero activity)
        voxel = fmri_dat[basic_mask, :].T

        # zooms are x, y, z, t
        tr = fmri_im.header.get_zooms()[3]

        # highpass filter voxel timeseries appropriately
        if er_csfmask is not None:
            # csf regressor is the mean of all voxels in the csf
            # mask at each time point
            lv_im = nb.load(er_csfmask)
            lvm = lv_im.get_data()
            lv_ts = fmri_dat[lvm != 0, :].T
            csf_reg = lv_ts.mean(axis=1)
        else:
            csf_reg = None 

        lc_voxel = self.linear_reg(voxel, csf_reg = csf_reg)

        nuis_voxel = self.freq_filter(lc_voxel, tr, highpass=highpass, lowpass=lowpass)
        # put the nifti back together again and re-transpose
        fmri_dat[basic_mask, :] = nuis_voxel.T
        img = nb.Nifti1Image(fmri_dat,
                             header=fmri_im.header,
                             affine=fmri_im.affine)
        # save the corrected image
        nb.save(img, nuisance_mri)
        pass
