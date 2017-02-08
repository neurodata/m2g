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

# qa_regdti.py
# Created by Vikram Chandrashekhar.
# Edited by Greg Kiar.
# Email: Greg Kiar @ gkiar@jhu.edu

import os
import re
import sys
import numpy as np
import nibabel as nb
import ndmg.utils as mgu
from argparse import ArgumentParser
from scipy import ndimage
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
mpl.use('Agg')  # very important above pyplot import

import matplotlib.pyplot as plt


def reg_dti_pngs(dti, gtab, atlas, outdir):
    """
    outdir: directory where output png file is saved
    fname: name of output file WITHOUT FULL PATH. Path provided in outdir.
    """

    atlas_data = nb.load(atlas).get_data()
    dti_data = nb.load(dti).get_data()
    b0_data = mgu().get_b0(gtab, dti_data)

    cmap1 = LinearSegmentedColormap.from_list('mycmap1', ['black', 'magenta'])
    cmap2 = LinearSegmentedColormap.from_list('mycmap2', ['black', 'green'])

    fig = plot_overlays(atlas_data, b0_data, (cmap1, cmap2))

    # name and save the file
    fname = os.path.split(dti)[1].split(".")[0] + '.png'
    plt.savefig(outdir + '/' + fname, format='png')


def plot_overlays(atlas, b0, cmaps):
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})

    if b0.shape == (182, 218, 182):
        x = [78, 90, 100]
        y = [82, 107, 142]
        z = [88, 103, 107]
    else:
        shap = b0.shape
        x = [int(shap[0]*0.35), int(shap[0]*0.51), int(shap[0]*0.65)]
        y = [int(shap[1]*0.35), int(shap[1]*0.51), int(shap[1]*0.65)]
        z = [int(shap[2]*0.35), int(shap[2]*0.51), int(shap[2]*0.65)]
    coords = (x, y, z)

    labs = ['Sagittal Slice (YZ fixed)',
            'Coronal Slice (XZ fixed)',
            'Axial Slice (XY fixed)']
    var = ['X', 'Y', 'Z']
    # create subplot for first slice
    # and customize all labels
    idx = 0
    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = plt.subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(b0[pos, :, :], 90)
                atl = ndimage.rotate(atlas[pos, :, :], 90)
            elif i == 1:
                image = ndimage.rotate(b0[:, pos, :], 90)
                atl = ndimage.rotate(atlas[:, pos, :], 90)
            else:
                image = b0[:, :, pos]
                atl = atlas[:, :, pos]

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0]/2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1]/2, image.shape[1] - 1])

            min_val, max_val = get_min_max(image)
            plt.imshow(atl, interpolation='none', cmap=cmaps[0], alpha=0.5)
            plt.imshow(image, interpolation='none', cmap=cmaps[1], alpha=0.5,
                       vmin=min_val, vmax=max_val)

    fig = plt.gcf()
    fig.set_size_inches(12.5, 10.5, forward=True)
    return fig


def get_min_max(data):
    '''
    data: regdti data to threshold.
    '''
    min_val = np.percentile(data, 2)
    max_val = np.percentile(data, 95)
    return (min_val, max_val)
