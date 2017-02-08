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
# Edited by Greg Kiar.
# Email: Greg Kiar @ gkiar@jhu.edu

from dipy.reconst.dti import fractional_anisotropy, color_fa
from argparse import ArgumentParser
from scipy import ndimage
import os
import re
import numpy as np
import nibabel as nb
import sys
import matplotlib

matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt


def tensor2fa(tensors, tensor_name, dti, derivdir, qcdir):
    '''
    outdir: location of output directory.
    fname: name of output fa map file. default is none (name created based on
    input file)
    '''
    dti_data = nb.load(dti)
    affine = dti_data.get_affine()
    dti_data = dti_data.get_data()

    # create FA map
    FA = fractional_anisotropy(tensors.evals)
    FA[np.isnan(FA)] = 0

    # generate the RGB FA map
    FA = np.clip(FA, 0, 1)
    RGB = color_fa(FA, tensors.evecs)

    fname = os.path.split(tensor_name)[1].split(".")[0] + '_fa_rgb.nii.gz'
    fa = nb.Nifti1Image(np.array(255 * RGB, 'uint8'), affine)
    nb.save(fa, derivdir + fname)

    fa_pngs(fa, fname, qcdir)


def fa_pngs(data, fname, outdir):
    '''
    data: fa map
    '''
    im = data.get_data()
    fig = plot_rgb(im)
    fname = os.path.split(fname)[1].split(".")[0] + '.png'
    plt.savefig(outdir + fname, format='png')


def plot_rgb(im):
    plt.rcParams.update({'axes.labelsize': 'x-large',
                         'axes.titlesize': 'x-large'})

    if im.shape == (182, 218, 182):
        x = [78, 90, 100]
        y = [82, 107, 142]
        z = [88, 103, 107]
    else:
        shap = im.shape
        x = [int(shap[0]*0.35), int(shap[0]*0.51), int(shap[0]*0.65)]
        y = [int(shap[1]*0.35), int(shap[1]*0.51), int(shap[1]*0.65)]
        z = [int(shap[2]*0.35), int(shap[2]*0.51), int(shap[2]*0.65)]
    coords = (x, y, z)

    labs = ['Sagittal Slice (YZ fixed)',
            'Coronal Slice (XZ fixed)',
            'Axial Slice (XY fixed)']
    var = ['X', 'Y', 'Z']

    idx = 0
    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = plt.subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(im[pos, :, :], 90)
            elif i == 1:
                image = ndimage.rotate(im[:, pos, :], 90)
            else:
                image = im[:, :, pos]

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0]/2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1]/2, image.shape[1] - 1])

            plt.imshow(image)

    fig = plt.gcf()
    fig.set_size_inches(12.5, 10.5, forward=True)
    return fig
