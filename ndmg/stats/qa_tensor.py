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

# qa_tensor.py
# Created by Vikram Chandrashekhar.
# Email: Greg Kiar @ gkiar@jhu.edu

from dipy.reconst.dti import fractional_anisotropy, color_fa
from argparse import ArgumentParser
from scipy import ndimage
import os
import re
import numpy as np
import nibabel as nib
import sys
import matplotlib

matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt


def tensor2fa(fs, outdir, fname=None):
    '''
    fs: of 2-tuples containing the tensor file and regdti file
    outdir: location of output directory.
    fname: name of output fa map file. default is none (name created based on
    input file)
    '''
    # load dti file
    ften, fdti = fs
    img = nib.load(fdti)
    dti_data = img.get_data()

    # load tensor file and grab data
    with np.load(ften) as data:
        tensor_fit = data['arr_0']
        tensor_fit = tensor_fit.tolist()

    # create FA map
    FA = fractional_anisotropy(tensor_fit.evals)
    # get rid of NaNs
    FA[np.isnan(FA)] = 0
    # check if fname is defined
    if fname is None:
        fname = os.path.split(ften)[1].split(".")[0] + '_fa_rgb.nii.gz'
    if outdir is None:
        outdir = './'
    # generate the RGB FA map
    FA = np.clip(FA, 0, 1)
    RGB = color_fa(FA, tensor_fit.evecs)
    # save the RGB FA map
    nib.save(nib.Nifti1Image(np.array(255 * RGB, 'uint8'), img.affine),
             outdir + fname)
    # return path of file
    return outdir + fname


def save_fa_png(fa_file, outdir, fname=None):
    '''
    fa_file: path to fa map file
    '''
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})

    # helper function to make sure that slices are plotted on the same figure
    def create_subplot(number, title, ylabel=None, xlabel=None, set_ticks=None,
                       set_ticklabels=False):
        ax = plt.subplot(number)
        ax.set_title(title)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if set_ticks is not None:
            ax.xaxis.set_ticks(set_ticks[0])
            ax.yaxis.set_ticks(set_ticks[1])
        if set_ticklabels:
            ax.get_yaxis().set_ticklabels([])
            ax.get_xaxis().set_ticklabels([])
        return ax
    img = nib.load(fa_file)
    data = img.get_data()
    ax_x1 = create_subplot(331, 'X = 78',
                           ylabel='Sagittal Slice: Y and Z fixed',
                           set_ticks=([0, data.shape[1]/2, data.shape[1] - 1],
                                      [0, data.shape[2]/2, data.shape[2] - 1]))
    plt.imshow(ndimage.rotate(data[78, :, :], 90))
    ax_x2 = create_subplot(332, 'X = 90', set_ticklabels=True)
    plt.imshow(ndimage.rotate(data[90, :, :], 90))
    ax_x3 = create_subplot(333, 'X = 100', set_ticklabels=True)
    plt.imshow(ndimage.rotate(data[100, :, :], 90))
    ax_y1 = create_subplot(334, 'Y = 82',
                           ylabel='Coronal Slice: X and Z fixed',
                           set_ticks=([0, data.shape[0]/2, data.shape[0] - 1],
                                      [0, data.shape[2]/2, data.shape[2] - 1]))
    plt.imshow(ndimage.rotate(data[:, 82, :], 90))
    ax_y2 = create_subplot(335, 'Y = 107', set_ticklabels=True)
    plt.imshow(ndimage.rotate(data[:, 107, :], 90))
    ax_y3 = create_subplot(336, 'Y = 142', set_ticklabels=True)
    plt.imshow(ndimage.rotate(data[:, 142, :], 90))
    ax_z1 = create_subplot(337, 'Z = 88',
                           ylabel='Axial Slice: X and Y fixed',
                           set_ticks=([0, data.shape[0]/2, data.shape[0] - 1],
                                      [0, data.shape[1]/2, data.shape[1] - 1]))
    plt.imshow(data[:, :, 88])
    ax_z2 = create_subplot(338, 'Z = 103', set_ticklabels=True)
    plt.imshow(data[:, :, 103])
    ax_z3 = create_subplot(339, 'Z = 107', set_ticklabels=True)
    plt.imshow(data[:, :, 107])
    fig = plt.gcf()
    fig.set_size_inches(12.5, 10.5, forward=True)
    if fname is None:
        fname = os.path.split(fa_file)[1].split(".")[0] + '.png'
    plt.savefig(outdir + fname, format='png')
    print(fname + " saved!")


def main():
    """
    Argument parser.
    Required parameters:
        tenfile:
            - Path to tensor file
        dtifile:
            - Path to regdti file
        faoutdir:
            - Path to fa map save location
        pngoutdir:
            - Path to fa png save location
    """
    parser = ArgumentParser(description="Computes FA maps and saves FA slices")
    parser.add_argument("tenfile", action="store", help="path to tensor file")
    parser.add_argument("dtifile", action="store", help="path to regdti file")
    parser.add_argument("faoutdir", action="store", help="output directory"
                        " for fa map")
    parser.add_argument("pngoutdir", action="store", help="output directory"
                        " for png")
    result = parser.parse_args()

    if (not os.path.isdir(result.faoutdir)):
        os.mkdir(result.faoutdir)
    if (not os.path.isdir(result.pngoutdir)):
        os.mkdir(result.pngoutdir)
    fafile = tensor2fa((result.tenfile, result.dtifile), result.faoutdir)
    save_fa_png(fafile, result.pngoutdir)

if __name__ == '__main__':
    main()
