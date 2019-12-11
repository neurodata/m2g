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

# qa_utils.py
# Created by Wilson Tang

import numpy as np


def get_min_max(data, minthr=2, maxthr=95):
    """
    Parameters
    -----------
    data: np array
        3-d regmri data to threshold.
    minthr: int
    maxthr: int

    Returns
    -----------
    min_max: tuple
        tuple of minimum and maximum values
    """
    min_val = np.percentile(data, minthr)
    max_val = np.percentile(data, maxthr)

    min_max = (min_val.astype(float), max_val.astype(float))
    return min_max


def opaque_colorscale(basemap, reference, vmin=None, vmax=None, alpha=1):
    """
    A function to return a colorscale, with opacities
    dependent on reference intensities.

    Parameter
    ---------
    basemap: matplotlib colormap
        the colormap to use for this colorscale.
    reference: np array
        the reference matrix.
    Returns
    ---------
    cmap = matplotlib colormap
    """
    reference = reference
    if vmin is not None:
        reference[reference > vmax] = vmax
    if vmax is not None:
        reference[reference < vmin] = vmin
    cmap = basemap(reference)
    maxval = np.nanmax(reference)
    # all values beteween 0 opacity and 1
    opaque_scale = alpha * reference / float(maxval)
    # remaps intensities
    cmap[:, :, 3] = opaque_scale
    return cmap


def pad_im(image, max_dim, pad_val, rgb):
    """
    Pads an image to be same dimensions as given max_dim

    Parameters
    -----------
    image: np array
        image object can be multiple dimensional or a slice.
    max_dim: int
        dimension to pad up to
    pad_val: int
        value to pad with.
    rgb: boolean
        flag to indicate if RGB and last dimension should not be padded
    Returns
    -----------
    padded_image: np array
        image with padding
    """
    pad_width = []
    for i in range(image.ndim):
        pad_width.append(((max_dim - image.shape[i]) // 2, (max_dim - image.shape[i]) // 2))
    if rgb:
        pad_width[-1] = (0, 0)

    # convert to tuple
    pad_width = tuple(pad_width)
    padded_image = np.pad(image, pad_width=pad_width, mode='constant', constant_values=pad_val)

    return padded_image