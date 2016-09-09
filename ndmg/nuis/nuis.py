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

# preproc.py
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

    def calc_residuals(self, mri, nuisance_mri):
        """
        A function that applies nuisance correction for linear
        and quadratic drift. Adjusts the CPAC function found here:
        http://fcp-indi.github.io/docs/developer/_modules/CPAC/
        nuisance/nuisance.html

        **Positional Arguments:**
            mri: the mri file.
            nuisance_mri: the nuisance corrected filename.
        """
        mri_im = nb.load(mri)
        mri_dat = mgu().get_brain(mri_im)

        region_mask = (mri_dat != 0).sum(-1) != 0
        # Calculate regressors
        # regressor_map = {'constant' : np.ones((mri_dat.shape[3],1))}
        # if(selector['compcor']):
        #   print 'compcor_ncomponents ', compcor_ncomponents
        #   regressor_map['compcor'] = calc_compcor_components(
        #            mri_dat, compcor_ncomponents, wm_sigs, csf_sigs)

        nvol = mri_dat.shape[3]
        X = np.zeros((nvol, 1))
        linear = np.arange(0, nvol)
        quad = np.arange(0, nvol)**2
        # ncomp = calc_compcor_components(mri_dat, 5, )
        for rval in [linear, quad]:
            X = np.hstack((X, rval.reshape(rval.shape[0], -1)))
        
        X = X[:, 1:]

        Y = mri_dat[region_mask].T
        B = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(Y)
        Y_res = Y - X.dot(B)

        mri_dat[region_mask] = Y_res.T

        new_img = nb.Nifti1Image(mri_dat, header=mri_im.get_header(),
                                 affine=mri_im.get_affine())

        nb.save(new_img, nuisance_mri)
        pass
