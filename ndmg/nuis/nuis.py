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
        # remove the voxels that are unchanging, as normalizing
        # these by std would lead to a divide by 0
        voxel = voxel[:, voxel.std(0) != 0]
        voxel = voxel - voxel.mean(axis=0)
        # normalize the signal
        voxel = np.divide(voxel, voxel.std(0))
        # returns the normalized signal
        return voxel

    def compcor(self, masked_ts, n=None, t=None, qcdir=None):
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
            qcdir:
                - an optional argument for passing a directory
                  to place quality control information.
        """
        # normalize the signal to mean center
        masked_ts = self.normalize_signal(masked_ts)
        # singular value decomposition to get the ordered
        # principal components
        (U, s, V) = np.linalg.svd(masked_ts, full_matrices=False)
        if qcdir is not None:
            # TODO add QC stuff with s
            pass
        if n is not None and t is not None:
            raise ValueError('CompCor: you have passed both a number of
                              components and a threshold. You should only pass
                              one or the other, not both.')
        else if n is not None:
            # return the top n principal components
            return U[:, 0:n]
        else if t is not None:
            # TODO add thresholding
            pass
        else:
            raise ValueError('CompCor: you have not passed a threshold nor
                              a number of components. You must specify one.')
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
        pass

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
        # OLS solution for GLM B = (X^TX)^(-1)X^TY
        coefs = np.linalg.inv(R.T.dot(R)).dot(R.T).dot(data)
        return R.dot(coefs)

    def segment_anat(self, amri, an, basename):
        """
        A function to use FSL's FAST to segment an anatomical
        image into GM, WM, and CSF masks.

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
        # run FAST, with options -t for the image type and -n to
        # segment into CSF (pve_0), WM (pve_1), GM (pve_2)
        cmd = " ".join(["fast -t", int(an), "-n 3 -o", basename, amri])
        mgu().execute_cmd(cmd)
        pass

    def extract_mask(self, prob_map, t, v):
        """
        A function to extract a mask from a probability map.
        Also, performs mask erosion.

        **Positional Arguments:**
            - prob_map:
                - the path to probability map for the given class
                  of brain tissue.
            - t:
                - the threshold to consider voxels part of the class.
            - v:
                - the number of voxels to erode.
        """
        prob = nb.load(prob_map)
        prob_dat = prob.get_data()
        mask = (prob_dat > t).astype(int)
        # TODO: mask erosion
        return mask

    def nuis_correct(self, fmri, amri, amask, an, lvmask, nuisance_mri,
                     basename, outdir, qcdir):
        """
        A function for nuisance correction on an aligned fMRI
        image. So far, this only highpass filters.

        **Positional Arguments:**
            fmri:
                - the path to an fMRI.
            amri:
                - the path to the anatomical MRI.
            amask:
                - the path to the anatomical mask we registered with.
            an:
                - an integer representing the type of the anatomical image.
                  (1 for T1w, 2 for T2w, 3 for PD).
            nuisance_mri:
                - the path where the nuisance MRI will be created.
            basename:
                - the name to use for files. Should be dataset_sub.
            outdir:
                - the base directory to place temporary files,
                  with no trailing /.
            qcdir:
                - the directory in which nuisance correction qc will be
                  placed, with no trailing /.
        """
        # load images as nibabel objects
        fmri_im = nb.load(fmri)
        amri_im = nb.load(amri)
        amask_im = nb.load(amask)
        nuisname = "".join([basename, "_nuis"])

        fmri_dat = fmri_im.get_data()[amask, :]
        # load the voxel timeseries and transpose
        voxel = fmri.get_data().T
        maskpath = outdir + "/" + basename + "_mask"
        segment_anat(amri, an, maskpath)

        # FAST will place the white matter probability map here
        wm_prob = maskpath + "_pve_2.nii.gz"
        wmm = self.extract_mask(wm_prob, .99, 2).T
        # extract the timeseries of white matter regions and transpose
        wm_ts = fmri_dat[wmm == 1, :].T
        # load the lateral ventricles CSF timeseries
        lv_ts = fmri_dat[lvmask == 1, :].T
        # time dimension is now the 0th dim
        t = voxel.shape[0]

        # linear drift regressor
        lin_reg = np.linspace(0, t)
        # quadratic drift regressor
        quad_reg = np.array(np.linspace(0, t)**2
        # csf regressor is the mean of all voxels in the csf
        # mask at each time point
        csf_reg = lv_ts.mean(axis=0)
        # white matter regressor is the top 5 components
        # in the white matter
        wm_reg = self.compcor(wm_ts, n=5)
        # use GLM model given regressors to approximate the weight we want
        # to regress out
        W = self.regress_signal(voxel, wm_reg)
        # nuisance ts is the difference btwn the original timeseries and
        # our regressors, and then we transpose back
        nuis_voxel = (voxel - W).T
        # put the nifti back together again
        fmri_dat[amask, :] = nuis_voxel
        img = nb.Nifti1Image(fmri_dat,
                             header = fmri_im.header,
                             affine = fmri_im.get_affine())
        # save the corrected image
        nb.save(img, nuisance_mri)
        pass
