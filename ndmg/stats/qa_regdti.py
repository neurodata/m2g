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
# Email: Greg Kiar @ gkiar@jhu.edu

import os
import re
import sys
import numpy as np
import nibabel as nib
from argparse import ArgumentParser
from matplotlib.colors import colorConverter
from skimage.filters import threshold_otsu
from scipy import ndimage
from matplotlib.colors import LinearSegmentedColormap
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs
import matplotlib as mpl
mpl.use('Agg')  # very important above pyplot import

import matplotlib.pyplot as plt


def save_reg_pngs(fs, outdir, fname=None):
    """
    fs: 4-tuple of paths to regdti, bval, bvec, and atlas files
    outdir: directory where output png file is saved
    fname: name of output file WITHOUT FULL PATH. Path provided in outdir.
    """
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})
    # unpack the files from the tuple
    fdti, fbval, fbvec, fatlas = fs
    # load atlas file and extract data
    atlas_img = nib.load(fatlas)
    atlas_data = atlas_img.get_data()
    # set the slice numbers you want to visualize
    # for each of the 3 dimensions
    x1 = 78
    x2 = 90
    x3 = 100
    y1 = 82
    y2 = 107
    y3 = 142
    z1 = 88
    z2 = 103
    z3 = 107
    # load dti file and extract data
    img = nib.load(fdti)
    data = img.get_data()
    # making sure the image displayed is the
    # brain without any magnetic gradent applied
    data = get_b0_vol(data, fbval, fbvec)

    # creating the two custom colormaps
    cmap1 = LinearSegmentedColormap.from_list('mycmap1', ['black', 'magenta'])
    cmap2 = LinearSegmentedColormap.from_list('mycmap2', ['black', 'green'])

    # create subplot for first slice
    # and customize all labels
    ax_x1 = plt.subplot(331)
    ax_x1.set_ylabel('Sagittal Slice: Y and Z fixed')
    ax_x1.set_title('X = ' + str(x1))
    ax_x1.yaxis.set_ticks([0, data.shape[2]/2, data.shape[2] - 1])
    ax_x1.xaxis.set_ticks([0, data.shape[1]/2, data.shape[1] - 1])
    image = data[x1, :, :, 0]
    # get the intensity value of the 3rd  and 98th percentiles (as min_val
    # and max_val, respectively) important to reduce impact of outliers on
    # intensity of image
    min_val, max_val = get_min_max(image)
    # displaying the images with atlas image using magenta and regdti using
    # green colormaps
    plt.imshow(ndimage.rotate(atlas_data[x1, :, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    # repeating above for each of the following slices
    ax_x2 = plt.subplot(332)
    ax_x2.set_title('X = ' + str(x2))
    ax_x2.get_yaxis().set_ticklabels([])
    ax_x2.get_xaxis().set_ticklabels([])
    image = data[x2, :, :, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[x2, :, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    ax_x3 = plt.subplot(333)
    ax_x3.set_title('X = ' + str(x3))
    ax_x3.get_yaxis().set_ticklabels([])
    ax_x3.get_xaxis().set_ticklabels([])
    image = data[x3, :, :, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[x3, :, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y1 = plt.subplot(334)
    ax_y1.set_ylabel('Coronal Slice: X and Z fixed')
    ax_y1.set_title('Y = ' + str(y1))
    ax_y1.yaxis.set_ticks([0, data.shape[0]/2, data.shape[0] - 1])
    ax_y1.xaxis.set_ticks([0, data.shape[2]/2, data.shape[2] - 1])
    image = data[:, y1, :, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:, y1, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y2 = plt.subplot(335)
    ax_y2.set_title('Y = ' + str(y2))
    ax_y2.get_yaxis().set_ticklabels([])
    ax_y2.get_xaxis().set_ticklabels([])
    image = data[:, y2, :, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:, y2, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y3 = plt.subplot(336)
    ax_y3.set_title('Y = ' + str(y3))
    ax_y3.get_yaxis().set_ticklabels([])
    ax_y3.get_xaxis().set_ticklabels([])
    image = data[:, y3, :, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:, y3, :], 90), interpolation='none',
               cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    ax_z1 = plt.subplot(337)
    ax_z1.set_ylabel('Axial Slice: X and Y fixed')
    ax_z1.set_title('Z = ' + str(z1))
    ax_z1.yaxis.set_ticks([0, data.shape[0]/2, data.shape[0] - 1])
    ax_z1.xaxis.set_ticks([0, data.shape[1]/2, data.shape[1] - 1])
    image = data[:, :, z1, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:, :, z1], interpolation='none', cmap=cmap1,
               alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)

    ax_z2 = plt.subplot(338)
    ax_z2.set_title('Z = ' + str(z2))
    ax_z2.get_yaxis().set_ticklabels([])
    ax_z2.get_xaxis().set_ticklabels([])
    image = data[:, :, z2, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:, :, z2], interpolation='none', cmap=cmap1,
               alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)

    ax_z3 = plt.subplot(339)
    ax_z3.set_title('Z = ' + str(z3))
    ax_z3.get_yaxis().set_ticklabels([])
    ax_z3.get_xaxis().set_ticklabels([])
    image = data[:, :, z3, 0]
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:, :, z3], interpolation='none', cmap=cmap1,
               alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2,
               vmin=min_val, vmax=max_val, alpha=0.5)
    # getting the current figure which has all the slices plotted on it
    fig = plt.gcf()
    fig.set_size_inches(12.5, 10.5, forward=True)
    # name and save the file
    if fname is None:
        fname = os.path.split(fdti)[1].split(".")[0] + '.png'
    plt.savefig(outdir + '/' + fname, format='png')
    print(fname + " saved!")


def get_min_max(data):
    '''
    data: regdti data to threshold.
    '''
    min_val = np.percentile(data, 3)
    max_val = np.percentile(data, 92)
    return (min_val, max_val)


def get_b0_vol(data, fbval, fbvec):
    '''
    data: 4D regdti data
    fbval: path to bval file
    fbvec: path to bvec file
    '''
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    # make sure that all bvecs are unit vectors
    normalize_bvecs(bvecs)
    gtab = gradient_table(bvals, bvecs)
    # return the 0-gradient volume
    return data[:, :, :, gtab.b0s_mask]


def normalize_bvecs(bvecs):
    '''
    bvecs: (N,3) array of bvecs
    '''
    for i in range(bvecs.shape[0]):
        norm = np.linalg.norm(bvecs[i, :])
        # if not unit length, normalize
        if norm is not 1 or norm is not 0:
            bvecs[i, :] = bvecs[i, :]/norm


def main():
    """
    Argument parser.
    Required parameters:
        dtifile:
            - path to regdti file
        bvalfile:
            - path to bval file
        bvecfile:
            - path to bvec file
        atlasfile:
            - path to atlas file
        outdir:
            - output file save directory
    """
    parser = ArgumentParser(description="Generates registration QA images")
    parser.add_argument("dtifile", action="store", help="base directory loc")
    parser.add_argument("bvalfile", action="store", help="base directory loc")
    parser.add_argument("bvecfile", action="store", help="base directory loc")
    parser.add_argument("atlasfile", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    result = parser.parse_args()

    # create the output directory if it doesn't exist
    if (not os.path.isdir(result.outdir)):
        os.mkdir(result.outdir)
    # do all the processing and save the output png file
    save_reg_pngs((result.dtifile, result.bvalfile, result.bvecfile,
                   result.atlasfile), result.outdir)


if __name__ == '__main__':
    main()
