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
# from CPAC.nuisance import calc_compcor_components
import nibabel as nb
import numpy as np


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
                  with dimensions [nvoxels, ntimesteps].
        """
        # remove the mean
        voxel = voxel - np.mean(voxel, axis=1)
        # normalize the signal
        voxel = np.divide(voxel, voxel.max(axis=1) - voxel.min(axis=1)[:, None])
        # replace nan entries with 0s, since we can have voxels
        # that are masked in but contain no data that would have
        # max - min = 0, and then divide by zero, in the prev step
        voxel[np.isnan(voxel)] = 0
        # returns the normalized signal
        return voxel

    def PCA(self, data, ncomponents=10):
        """
        A function to perform principal component
        analysis on a voxel timeseries.

        **Positional Arguments:**
            data:
                - the data to perform PCA on.
            ncomponents:
                - the number of components we wish
                  to keep.
        """
        print "Performing Principal Component Analysis..."
        U, s, V = np.linalg.svd(data, full_matrices=False)

        print "Extracting top " + str(ncomponents) + "Components..."
        return U[:,0:ncomponents], s

    def CompCor(self, data, regressor_masks, ncomponents=10):
        """
        A function to perform CompCor given a list of regressor
        masks.
    
        **Positional Arguments:**
            data:
                - the data to perform compcor on.
            regressor_masks:
                - a list of regressor masks to include.
            ncomponents:
                - the number of components to calculate.
        """
        pass
        

    def highpass_filter(self, mri, bandpass_mri):
        """
        A function that uses FSL's fslmaths to high pass
        an fMRI image.

        **Positional Arguments:**
            mri:
                - the unfiltered image.
            bandpass_mri:
                - the image with low frequency signal removed.
        """
        mri_im = nb.load(mri)
        highpass = 1/.01 # above this freq we want to include
        low = -1 # below this freq we want to include, -1
                 # includes all (ignore low pass)
        tr = mri_im.header.get_zooms()[3]
        sigma_high = highpass/(2*tr)

        cmd = "fslmaths " + mri + " -bptf " + str(sigma_high) + " " +\
            str(low) + " " + bandpass_mri
        mgu().execute_cmd(cmd)

    def regress_signal(self, data, W):
        """
        Regresses data to given regressors.

        **Positional Arguments:**
            - data:
                - the data as a ndarray.
            - W:
                - a numpy ndarray of regressors to
                  regress to.
        """
        # OLS solution for GLM B = (X^TX)^(-1)X^TY
        coefs = np.linalg.inv(W.T.dot(W)).dot(W.T).dot(data)
        return W.dot(coefs)

    def nuis_correct(self, mri, nuisance_mri, outdir, mask=None,
                     regressor_masks=[]):
        """
        A function for nuisance correction on an aligned fMRI
        image. So far, this only highpass filters.

        **Positional Arguments:**
            mri:
                - the mri file.
            nuisance_mri:
                - the nuisance corrected filename.
            outdir:
                - the base output directory to place outputs.
            mask:
                - the mask with which to consider timeseries.
                  If None, simply ignore voxels with values of 0.
        """
        fmri_name = mgu().get_filename(mri)

        highpass_im = mgu().name_tmps(outdir, fmri_name, "_highpass.nii.gz")
        self.highpass_filter(mri, highpass_im)

        mgu().execute_cmd("cp " + highpass_im + " " + nuisance_mri)
#         uncorrected = nb.load(highpass_im)
#         fmri_data = uncorrected.get_data()
# 
#         if mask is None:
#             # use a mask that masks voxels with no data over
#             # the timecourse
#             maskbool = ((fmri_data != 0).sum(-1) != 0)
#         else:
#             mask = mgu().get_braindata(mask)
#             maskbool = (mask > 0)
#         # get the voxel timecourse inside of the mask
#             voxel_ts = fmri_data[mask, :]
#         # normalize the signal to improve our nuisance steps, as
#         # SVD performs best on normalized data
#         # note that we transpose in this step, and will un-transpose when
#         # we are done, as SVD operates natively on the transpose
#         # of our data.
#         voxel_ts = self.normalize_signal(voxel_ts).T
# 
#         # perform comp cor on top 5 components
#         if regressor_masks:
#             CompCor_regressors = self.CompCor(voxel_ts, regressor_masks,
#                                               ncomponents=5)
#             # regress the signal to the CompCor regressors
#             compcor_regressed = self.regress_signal(voxel_ts,
#                                                     CompCor_regressors)
#             # and then regress these away
#             voxel_ts = voxel_ts - compcor_regressed
# 
#         # perform PCA to preserve maximal variance
#         PCA_regressors = self.PCA(voxel_ts, ncomponents=10)
# 
#         # regress the signal to the PCA regressors
#         voxel_ts = self.regress_signal(voxel_ts, PCA_regressors)
# 
#         # put the brain back together again and un-transpose...
#         fmri_data[mask,:] = voxel_ts.T
#         # put back into a nifti image. We don't do anything that breaks
#         # headers or changes scaling, so use the same header and affine
#         # as previously.
#         img = nb.Nifti1Image(fmri_data, header = uncorrected.get_header(),
#                              affine = uncorrected.get_affine)
#         # save the nuisance corrected image
#         nb.save(img, nuisance_mri)
        pass
