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
# timeseries.py
# Created by Eric W Bridgeford on 2016-06-07.
# Email: ericwb95@gmail.com

import numpy as np
import nibabel as nb
import sys
from ndmg.utils import utils as mgu


class timeseries(object):

    def __init__(self):
        """
        Timeseries extraction class
        """
        pass

    def voxel_timeseries(self, func_file, mask_file, voxel_file=None):
        """
        Function to extract timeseries for the voxels in the provided
        mask.
        Returns the voxel timeseries as a numpy.ndarray.

        **Positional Arguments**

            func_file:
                - the path to the fmri 4d volume to extract timeseries.
                can be string, nifti1image, or ndarray
            mask_file:
                - the path to the binary mask the user wants to extract
                voxel timeseries over. Can be string, nifti1image, or
                ndarray
            voxel_file:
                - the path to the voxel timeseries to be created.
                Must be string. If None, don't save and just return
                the voxel timeseries.
        """
        print "Extracting Voxel Timeseries for " + str(func_file) + "..."

        # load the mask data
        maskdata = mgu.get_braindata(mask_file)
        maskbool = (maskdata > 0)  # extract timeseries for any labelled voxels

        # load the MRI data
        funcdata = mgu.get_braindata(func_file)
        # load all the voxel timeseries that are within the atlas mask
        voxel_ts = funcdata[maskbool, :]
        if voxel_file is not None:
            np.savez(voxel_file, voxel=voxel_ts)
        return voxel_ts

    def roi_timeseries(self, func_file, label_file, roits_file=None):
        """
        Function to extract average timeseries for the voxels in each
        roi of the labelled atlas.
        Returns the roi timeseries as a numpy.ndarray.

        **Positional Arguments**

            func_file:
                - the path to the 4d volume to extract timeseries
            label_file:
                - the path to the labelled atlas containing labels
                    for the voxels in the fmri image
            roits_file:
                - the path to where the roi timeseries will be saved. If
                None, don't save and just return the roi_timeseries.
        """
        labeldata = mgu.get_braindata(label_file)
        # rois are all the nonzero unique values the parcellation can take
        rois = np.sort(np.unique(labeldata[labeldata > 0]))
        funcdata = mgu.get_braindata(func_file)

        # initialize time series to [numrois]x[numtimepoints]
        roi_ts = np.zeros((len(rois), funcdata.shape[3]))
        # iterate over the unique possible rois. note that the rois
        # could have nonstandard values, so assign indices w enumerate
        for idx, roi in enumerate(rois):
            roibool = labeldata == roi  # get a bool where our voxels in roi
            roibool
            roi_vts = funcdata[roibool, :]
            # take the mean for the voxel timeseries, and ignore voxels with
            # no variance
            ts = roi_vts[roi_vts.std(axis=1) != 0, :].mean(axis=0)
            if ts.size != 0:
                roi_ts[idx, :] = ts

        if roits_file:
            np.savez(roits_file, roi=roi_ts)
        return roi_ts
