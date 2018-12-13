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

from __future__ import print_function

import numpy as np
import nibabel as nb
from dipy.reconst.dti import TensorModel, fractional_anisotropy, quantize_evecs
from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                   auto_response)
from dipy.direction import peaks_from_model
from dipy.tracking.eudx import EuDX
from dipy.data import get_sphere


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
