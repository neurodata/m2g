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
from ndmg.qc import qc as mgqc


class timeseries(object):

    def __init__(self):
        """
        Timeseries extraction class
        """
        pass

    def voxel_timeseries(self, fmri_file, mask_file, voxel_file=""):
        """
        Function to extract timeseries for the voxels in the provided
        mask.
        Returns the voxel timeseries as a numpy.ndarray.

        **Positional Arguments**
            - fmri_file: the path to the fmri 4d volume to extract timeseries.
                         can be string, nifti1image, or ndarray
            - mask_file: the path to the binary mask the user wants to extract
                    voxel timeseries over. Can be string, nifti1image, or
                    ndarray
            - voxel_file: the path to the voxel timeseries to be created.
                          Must be string.
        """
        print "Extracting Voxel Timeseries for " + str(fmri_file) + "..."

        # load the mask data
        maskdata = mgu().get_brain(mask_file)
        maskbool = (maskdata > 0)  # extract timeseries for any labelled voxels

        # load the MRI data
        fmridata = mgu().get_brain(fmri_file)
        voxel_ts = fmridata[maskbool, :]
        if voxel_file:
            np.savez(voxel_file, voxel_ts)
        return voxel_ts

    def roi_timeseries(self, fmri_file, label_file, roits_file="", qcdir=None,
                       scanid="", refid=""):
        """
        Function to extract average timeseries for the voxels in each
        roi of the labelled atlas.
        Returns the roi timeseries as a numpy.ndarray.

        **Positional Arguments**
            - fmri_file: the path to the 4d volume to extract timeseries
            - label_file: the path to the labelled atlas containing labels
                    for the voxels in the fmri image
            - roits_file: the path to where the roi timeseries will be saved
        """
        labeldata = mgu().get_brain(label_file)

        rois = np.sort(np.unique(labeldata[labeldata > 0]))

        fmridata = mgu().get_brain(fmri_file)

        # initialize so resulting ra is [numrois]x[numtimepoints]
        roi_ts = np.zeros((rois.shape[0], fmridata.shape[3]))

        for roi in rois:
            roi_idx = np.where(rois == roi)[0][0]  # the index of the roi

            roibool = (labeldata == roi)  # get a bool where our voxels in roi
            roi_voxelwisets = fmridata[roibool, :]

            print(roi_voxelwisets.shape)
            roi_ts[roi_idx, :] = np.mean(roi_voxelwisets, axis=0)

        if qcdir is not None:
            mgqc().image_align(fmridata, labeldata, qcdir=qcdir,
                               scanid=scanid, refid=refid)

        if roits_file:
            np.savez(roits_file, roi_ts)
        return roi_ts
