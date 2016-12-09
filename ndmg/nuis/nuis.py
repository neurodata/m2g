#/usr/bin/env python

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
from ndmg.stats import qc as mgqc
import scipy.signal as signal

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
        print t
        if n is not None and t is not None:
            raise ValueError('CompCor: you have passed both a number of \
                              components and a threshold. You should only pass \
                              one or the other, not both.')
        elif n is not None:
            # return the top n principal components
            return U[:, 0:n], s
        elif t is not None:
            var_per_comp = s/np.sum(s) # get percent variance of each component
            total_var = np.cumsum(var_per_comp)
            thresh_var = total_var[total_var > t]
            # return up to lowest component greater than threshold
            idx = np.argmin(thresh_var)
            return U[:, 0:idx], s
        else:
            raise ValueError('CompCor: you have not passed a threshold nor \
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
            if (x.shape == y.shape and
                y.shape == z.shape):
                # iterated over all the nonzero voxels
                for j in range(0, x.shape[0]):
                    # check that the 3d voxels within 1 voxel are 1
                    # if so, add to the new mask
                    md = mask.shape
                    if (mask[x[j],y[j],z[j]] and
                        mask[np.min((x[j]+1, md[0]-1)),y[j],z[j]] and
                        mask[x[j],np.min((y[j]+1, md[1]-1)),z[j]] and
                        mask[x[j],y[j],np.min((z[j]+1, md[2]-1))] and
                        mask[np.max((x[j]-1, 0)),y[j],z[j]] and
                        mask[x[j],np.max((y[j]-1, 0)),z[j]] and
                        mask[x[j],y[j],np.max((z[j]-1, 0))]):
                        erode_mask[x[j],y[j],z[j]] = 1
            else:
                raise ValueError('Your mask erosion has an invalid shape.')
            mask = erode_mask
        eroded_mask_img = nb.Nifti1Image(mask,
                                         header = mask_img.header,
                                         affine = mask_img.get_affine())
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
                             header = prob.header,
                             affine = prob.get_affine())
        # save the corrected image
        nb.save(img, mask_path)
        return mask

    def regress_nuisance(self, fmri, nuisance_mri, wmmask, lvmask, n=5, t=None,
                         qcdir=None):
        """
        Regresses Nuisance Signals from brain images. Note that this
        function assumes that you have exactly the masks you wish to use;
        no erosion or segmentation takes place here. See nuisance_correct
        for the implementation that goes from fmri and amri -> corrected.

        **Positional Arguments:**
            - fmri:
                - the path to a fmri brain as a nifti image.
            - nuisance_fmri:
                - the desired path for the nuisance corrected brain.
            - wmmask:
                - the path to a white matter mask (should be eroded ahead of time).
            - lvmask:
                - the path to a lateral ventricles mask.
            - n:
                - the number of components to consider for white matter regression.
            - t:
                - the expected variance to consider for white matter regression.
            - qcdir:
                - the quality control directory to place qc.
        """
        fmri_name = mgu().get_filename(fmri)
        fmri_im = nb.load(fmri)

        lv_im = nb.load(lvmask)
        lvm = lv_im.get_data()

        wm_im = nb.load(wmmask)
        wmm = wm_im.get_data()

        fmri_dat = fmri_im.get_data()
        # load the voxel timeseries and transpose
        voxel = fmri_dat[fmri_dat.sum(axis=3) > 0, :].T
        # extract the timeseries of white matter regions and transpose
        wm_ts = fmri_dat[wmm != 0, :].T
        # load the lateral ventricles CSF timeseries
        lv_ts = fmri_dat[lvm != 0, :].T
        # time dimension is now the 0th dim
        time = voxel.shape[0]
        # linear drift regressor
        lin_reg = np.array(range(0, time))
        # quadratic drift regressor
        quad_reg = np.array(range(0, time))**2
        # csf regressor is the mean of all voxels in the csf
        # mask at each time point
        csf_reg = lv_ts.mean(axis=1)
        # white matter regressor is the top 5 components
        # in the white matter
        wm_reg, s = self.compcor(wm_ts, n=None, t=.1)
 
        if qcdir is not None:
            mgqc().expected_variance(s, wm_reg.shape[1], qcdir,
                                     scanid=fmri_name + "_compcor",
                                     title="CompCor")

        # use GLM model given regressors to approximate the weight we want
        # to regress out
        R = np.column_stack((np.ones(time), lin_reg, quad_reg, wm_reg, csf_reg))
        W = self.regress_signal(voxel, R)
        # nuisance ts is the difference btwn the original timeseries and
        # our regressors, and then we transpose back
        nuis_voxel = (voxel - W).T
        # put the nifti back together again
        fmri_dat[fmri_dat.sum(axis=3) > 0,:] = nuis_voxel
        img = nb.Nifti1Image(fmri_dat,
                             header = fmri_im.header,
                             affine = fmri_im.affine)
        # save the corrected image
        nb.save(img, nuisance_mri)
        pass

    def nuis_correct(self, fmri, amri, amask, an, lvmask, nuisance_mri,
                     outdir, qcdir=None):
        """
        A function for nuisance correction on an aligned fMRI
        image. This assumes we have purely registered brains,
        and a lateral ventricle mask, and does the rest of the work
        computing intermediates for you.

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
            outdir:
                - the base directory to place temporary files,
                  with no trailing /.
            qcdir:
                - the directory in which nuisance correction qc will be
                  placed, with no trailing /.
        """
        # load images as nibabel objects
        amask_im = nb.load(amask)
        amm = amask_im.get_data()

        anat_name = mgu().get_filename(amri)
        nuisname = "".join([anat_name, "_nuis"])


        map_path = mgu().name_tmps(outdir, nuisname, "_map")
        wmmask = mgu().name_tmps(outdir, nuisname, "_wm_mask.nii.gz")
        er_wmmask = mgu().name_tmps(outdir, nuisname, "_eroded_wm_mask.nii.gz")

        # segmetn the image into different classes of brain tissue
        self.segment_anat(amri, an, map_path)
        # FAST will place the white matter probability map here
        wm_prob = map_path + "_pve_2.nii.gz"
        self.extract_mask(wm_prob, wmmask, .99)
        self.erode_mask(wmmask, er_wmmask, 2)

        if qcdir is not None:
            # show the eroded white matter mask over the anatomical image
            # with different opaquenesses
            mgqc().mask_align(er_wmmask, amri, qcdir,
                              scanid=anat_name + "_eroded_wm", refid=anat_name)
            # show the eroded white mask over the original white matter mask
            mgqc().mask_align(er_wmmask, wmmask, qcdir,
                              scanid=anat_name + "_eroded_wm",
                              refid=anat_name + "_wm")

        self.regress_nuisance(fmri, nuisance_mri, er_wmmask, lvmask, n=None,
                              t=.1, qcdir=qcdir)
        pass
