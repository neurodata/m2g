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


# Created by Vikram Chandrashekhar.
# Edited by Greg Kiar, Eric Bridgeford and Chuankai Luo.
# Email: Greg Kiar @ gkiar@jhu.edu   cluo16@jhu.edu

import warnings

warnings.simplefilter("ignore")
import os
import re
import sys
import numpy as np
import nibabel as nb
# import ndmg.utils as mgu
from argparse import ArgumentParser
from scipy import ndimage
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

mpl.use("Agg")  # very important above pyplot import
from nilearn.plotting.edge_detect import _edge_map as edge_map
import matplotlib.pyplot as plt
from ndmg.utils.qa_utils import get_min_max, opaque_colorscale,pad_im
from ndmg.utils.gen_utils import get_filename, get_braindata





def gen_overlay_pngs(
    brain, original, outdir, loc=0, mean=False, minthr=2, maxthr=95, edge=False):
    """
    generate the image combine the brain and original data

    Parameters
    ----------
    brain:
        is the skull striped result, only left the brain
    original:
        is the original nii.gz file
    outdir:
        directory where output png file is saved
    loc and mean is to deal with 4d data
    minthr, maxthr, edge are the variables about the color
    """
    try:
        original_name = get_filename(original)
    except ValueError:
        original_name = 'stripped_brain_skull_comparison'
    brain_data = nb.load(brain).get_data()
    if brain_data.ndim == 4:  # 4d data, so we need to reduce a dimension
        if mean:
            brain_data = brain_data.mean(axis=3)
        else:
            brain_data = brain_data[:, :, :, loc]
    else:  # dim=3
        brain_data = brain_data

    cmap1 = LinearSegmentedColormap.from_list("mycmap1", ["white", "magenta"])
    cmap2 = LinearSegmentedColormap.from_list("mycmap2", ["white", "green"])


    fig = plot_overlays_skullstrip(brain_data, original, [cmap1, cmap2], minthr, maxthr, edge)

    # name and save the file
    fig.savefig(f"{outdir}/qa_skullstrip__{original_name}.png", format="png")





def plot_overlays_skullstrip(b0, original, cmaps=None, minthr=2, maxthr=95, edge=False):
    """
    generate the image combine the brain and original data

    Parameters
    ----------
    b0:
        is the skull striped result, only left the brain
    original:
        is the original nii.gz file
    cmaps, minthr, maxthr, edge are the variables about the color
    """

    plt.rcParams.update({"axes.labelsize": "x-large", "axes.titlesize": "x-large"})
    foverlay = plt.figure()

    original = get_braindata(original)
    ori_shape = get_braindata(b0).shape
    b0 = get_braindata(b0)
    if original.shape != b0.shape:
        raise ValueError("Two files are not the same shape.")
    b0 = pad_im(b0, max(ori_shape[0:3]), 0, False)
    original = pad_im(original,max(ori_shape[0:3]),0, False)


    if cmaps is None:
        cmap1 = LinearSegmentedColormap.from_list("mycmap1", ["white", "magenta"])
        cmap2 = LinearSegmentedColormap.from_list("mycmap2", ["white", "green"])
        cmaps = [cmap1, cmap2]

    x, y, z = get_true_volume(b0)
    coords = (x, y, z)

    labs = [
        "Sagittal Slice",
        "Coronal Slice",
        "Axial Slice",
    ]
    var = ["X", "Y", "Z"]
    # create subplot for first slice
    # and customize all labels
    idx = 0
    if edge:
        min_val = 0
        max_val = 1
    else:
        min_val, max_val = get_min_max(b0, minthr, maxthr)

    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = foverlay.add_subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(b0[pos, :, :], 90)
                atl = ndimage.rotate(original[pos, :, :], 90)
            elif i == 1:
                image = ndimage.rotate(b0[:, pos, :], 90)
                atl = ndimage.rotate(original[:, pos, :], 90)
            else:
                image = ndimage.rotate(b0[:, :, pos], 0)
                atl = ndimage.rotate(original[:, :, pos], 0)

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0] / 2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1] / 2, image.shape[1] - 1])
            if edge:
                image = edge_map(image).data
                image[image > 0] = max_val
                image[image == 0] = min_val
            # Set the axis invisible
            plt.xticks([])
            plt.yticks([])

            # Set the frame invisible
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.imshow(atl, interpolation="none", cmap=cmaps[0], alpha=0.9)
            ax.imshow(
                opaque_colorscale(
                    cmaps[1], image, alpha=0.9, vmin=min_val, vmax=max_val
                )
            )
            if idx ==3:
                plt.plot(0, 0, "-", c="magenta", label='skull')
                plt.plot(0, 0, "-", c="green", label='brain')
                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0, box.width, box.height*0.8])
                plt.legend(loc='best', fontsize=15, frameon=False, bbox_to_anchor=(1.5, 1.5))

    # Set title for the whole picture
    [a, b, c] = ori_shape
    title = 'QA For skullstrip. Scan Volume:' + str(a) + '*' + str(b) + '*' + str(c)
    foverlay.suptitle(title, fontsize=24)
    foverlay.set_size_inches(12.5, 10.5, forward=True)
    return foverlay

def get_true_volume(nparray):
    """
    locates 1/4,1/3,1/2 slices of brain and returns them
    """
    img_arr = nparray.astype(int)
    threshold = int(1)
    img_arr[img_arr <= threshold] = 0
    img_arr[img_arr > threshold] = 1
    true_volume = np.where(img_arr == 1)
    x = get_range(true_volume, 0)
    y = get_range(true_volume, 1)
    z = get_range(true_volume, 2)
    return x, y, z

def get_range(array,i):
    min_num = min(array[i])
    max_num = max(array[i])
    arrange = np.arange(min_num, max_num)
    quarter = np.percentile(arrange, [25, 50, 75]).astype(int)
    return quarter



def get_braindata(brain_file):
    """Opens a brain data series for a mask, mri image, or atlas.
    Returns a numpy.ndarray representation of a brain.
    Parameters
    ----------
    brain_file : str, nibabel.nifti1.nifti1image, numpy.ndarray
        an object to open the data for a brain. Can be a string (path to a brain file),
        nibabel.nifti1.nifti1image, or a numpy.ndarray
    Returns
    -------
    array
        array of image data
    Raises
    ------
    TypeError
        Brain file is not an accepted format
    """

    if type(brain_file) is np.ndarray:  # if brain passed as matrix
        braindata = brain_file
    else:
        if type(brain_file) is str or type(brain_file) is str:
            brain = nb.load(str(brain_file))
        elif type(brain_file) is nb.nifti1.Nifti1Image:
            brain = brain_file
        else:
            raise TypeError(
                "Brain file is type: {}".format(type(brain_file))
                + "; accepted types are numpy.ndarray, "
                "string, and nibabel.nifti1.Nifti1Image."
            )
        braindata = brain.get_data()
    return braindata