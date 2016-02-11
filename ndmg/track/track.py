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

from itertools import combinations
import numpy as np
import nibabel as nb
from dipy.reconst.dti import TensorModel, fractional_anisotropy, quantize_evecs
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                   auto_response)
from dipy.direction import peaks_from_model
from dipy.tracking.eudx import EuDX
from dipy.data import get_sphere, get_data
from dipy.core.gradients import gradient_table


class track():

    def __init__(self):
        """
        Tensor and fiber tracking class
        """
        # WGR:TODO rewrite help text
        pass

    def eudx_basic(self, dti_file, mask_file, gtab, stop_val=0.1):
        """
        Tracking with basic tensors and basic eudx - experimental
        We now force seeding at every voxel in the provided mask for
        simplicity.  Future functionality will extend these options.
        **Positional Arguments:**

                dti_file:
                    - File (registered) to use for tensor/fiber tracking
                mask_file:
                    - Brain mask to keep tensors inside the brain
                gtab:
                    - dipy formatted bval/bvec Structure

        **Optional Arguments:**
                stop_val:
                    - Value to cutoff fiber track
        """

        img = nb.load(dti_file)
        data = img.get_data()

        img = nb.load(mask_file)

        mask = img.get_data()

        # use all points in mask
        seedIdx = np.where(mask > 0)  # seed everywhere not equal to zero
        seedIdx = np.transpose(seedIdx)

        model = TensorModel(gtab)
        ten = model.fit(data, mask)
        sphere = get_sphere('symmetric724')
        ind = quantize_evecs(ten.evecs, sphere.vertices)
        eu = EuDX(a=ten.fa, ind=ind, seeds=seedIdx,
                  odf_vertices=sphere.vertices, a_low=stop_val)
        tracks = [e for e in eu]
        return (ten, tracks)

    def eudx_advanced(self, dti_file, mask_file, gtab,
                      seed_num=100000, stop_val=0.1):
        """
        Tracking with more complex tensors - experimental

        Initializes the graph with nodes corresponding to the number of ROIs

        **Positional Arguments:**

                dti_file:
                    - File (registered) to use for tensor/fiber tracking
                mask_file:
                    - Brain mask to keep tensors inside the brain
                gtab:
                    - dipy formatted bval/bvec Structure

        **Optional Arguments:**
                seed_num:
                    - Number of seeds to use for fiber tracking
                stop_val:
                    - Value to cutoff fiber track
        """

        img = nb.load(dti_file)
        data = img.get_data()

        img = nb.load(mask_file)

        mask = img.get_data()
        mask = mask > 0  # to ensure binary mask

        """
        For the constrained spherical deconvolution we need to estimate the
        response function (see :ref:`example_reconst_csd`) and create a model.
        """

        response, ratio = auto_response(gtab, data, roi_radius=10,
                                        fa_thr=0.7)

        csd_model = ConstrainedSphericalDeconvModel(gtab, response)

        """
        Next, we use ``peaks_from_model`` to fit the data and calculated
        the fiber directions in all voxels.
        """

        sphere = get_sphere('symmetric724')

        csd_peaks = peaks_from_model(model=csd_model,
                                     data=data,
                                     sphere=sphere,
                                     mask=mask,
                                     relative_peak_threshold=.5,
                                     min_separation_angle=25,
                                     parallel=True)

        """
        For the tracking part, we will use ``csd_model`` fiber directions
        but stop tracking where fractional anisotropy (FA) is low (< 0.1).
        To derive the FA, used as a stopping criterion, we need to fit a
        tensor model first. Here, we use weighted least squares (WLS).
        """
        print 'tensors...'

        tensor_model = TensorModel(gtab, fit_method='WLS')
        tensor_fit = tensor_model.fit(data, mask)

        FA = fractional_anisotropy(tensor_fit.evals)

        """
        In order for the stopping values to be used with our tracking
        algorithm we need to have the same dimensions as the
        ``csd_peaks.peak_values``. For this reason, we can assign the
        same FA value to every peak direction in the same voxel in
        the following way.
        """

        stopping_values = np.zeros(csd_peaks.peak_values.shape)
        stopping_values[:] = FA[..., None]

        streamline_generator = EuDX(stopping_values,
                                    csd_peaks.peak_indices,
                                    seeds=seed_num,
                                    odf_vertices=sphere.vertices,
                                    a_low=stop_val)

        streamlines = [streamline for streamline in streamline_generator]

        return streamlines

    def compute_tensors(self, dti_vol, atlas_file, gtab):
        # WGR:TODO figure out how to organize tensor options and formats
        # WGR:TODO figure out how to deal with files on disk vs. in workspace
        """
        Takes registered DTI image and produces tensors

        **Positional Arguments:**

                dti_vol:
                    - Registered DTI volume, from workspace.
                atlas_file:
                    - File containing an atlas (or brain mask).
                gtab:
                    - Structure containing dipy formatted bval/bvec information
        """

        labeldata = nib.load(atlas_file)

        label = labeldata.get_data()

        """
        Create a brain mask. Here we just threshold labels.
        """

        mask = (label > 0)

        gtab.info
        print data.shape
        """
        For the constrained spherical deconvolution we need to estimate the
        response function (see :ref:`example_reconst_csd`) and create a model.
        """

        response, ratio = auto_response(gtab, dti_vol, roi_radius=10,
                                        fa_thr=0.7)

        csd_model = ConstrainedSphericalDeconvModel(gtab, response)

        """
        Next, we use ``peaks_from_model`` to fit the data and calculated
        the fiber directions in all voxels.
        """

        sphere = get_sphere('symmetric724')

        csd_peaks = peaks_from_model(model=csd_model,
                                     data=data,
                                     sphere=sphere,
                                     mask=mask,
                                     relative_peak_threshold=.5,
                                     min_separation_angle=25,
                                     parallel=True)

        """
        For the tracking part, we will use ``csd_model`` fiber directions
        but stop tracking where fractional anisotropy (FA) is low (< 0.1).
        To derive the FA, used as a stopping criterion, we need to fit a
        tensor model first. Here, we use weighted least squares (WLS).
        """
        print 'tensors...'

        tensor_model = TensorModel(gtab, fit_method='WLS')
        tensor_fit = tensor_model.fit(data, mask)

        FA = fractional_anisotropy(tensor_fit.evals)

        """
        In order for the stopping values to be used with our tracking
        algorithm we need to have the same dimensions as the
        ``csd_peaks.peak_values``. For this reason, we can assign the
        same FA value to every peak direction in the same voxel in
        the following way.
        """

        stopping_values = np.zeros(csd_peaks.peak_values.shape)
        stopping_values[:] = FA[..., None]
        print datetime.now() - startTime
        pass

    def fibers_eudx(self, stopping_values, peak_indices, seeds,
                    odf_vertices, cutoff):
        # WGR:TODO figure out how to organize tensor options and formats
        # WGR:TODO figure out how to deal with files on disk vs. in workspace
        """
        Tensors are used to construct fibers

        **Positional Arguments:**

                dti_vol:
                    - Registered DTI volume, from workspace.
                atlas_file:
                    - File containing an atlas (or brain mask).
                gtab:
                    - Structure containing dipy formatted bval/bvec information
        """

        streamline_generator = EuDX(stopping_values,
                                    csd_peaks.peak_indices,
                                    seeds=10**6,
                                    odf_vertices=sphere.vertices,
                                    a_low=0.1)

        streamlines = [streamline for streamline in streamline_generator]

        return streamlines
