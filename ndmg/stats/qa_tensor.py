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
# Edited by Wilson Tang
# Email: Greg Kiar @ gkiar@jhu.edu

import warnings

warnings.simplefilter("ignore")
from dipy.reconst.dti import fractional_anisotropy, color_fa
from argparse import ArgumentParser
from scipy import ndimage
import os
import re
import numpy as np
import nibabel as nb
import sys
import matplotlib

from dipy.viz import window, actor
from fury.actor import orient2rgb

matplotlib.use("Agg")  # very important above pyplot import
import matplotlib.pyplot as plt


def generate_3_d_directions(peak_dirs,peak_values):
    """
    Generates 3-d data required for plotting directions for the entire brain volume
    
    Parameters
    -----------
    peak_dirs: np array of peak_dirs 
    peak_values: np array of peak_values
    slices: dictionary of lists of slices in x,y,z plane
    
    Returns
    -----------
    centers: np array of center points
    directions: np array of vector directions
    directions_colors: np array of RGB colors 
    heights: np array of vector magnitudes
    """
    
    #initialize 
    centers = []
    directions = []
    heights = []
    directions_colors = []
    
    #iteratively create required new arrow entries per value in 3-d peak object
    for x in range(peak_dirs.shape[0]):
        for y in range(peak_dirs.shape[1]): 
            for z in range(peak_dirs.shape[2]):
                centers.append([x,y,z])
                
                #relies on the fact that peaks_from_models generates peak_dirs and peak_values in descending order
                directions.append(peak_dirs[x,y,z,0,:])
                heights.append(peak_values[x,y,z,0])

    #convert to np arrays
    centers = np.asarray(centers)
    directions = np.asarray(directions)
    heights = np.asarray(heights)
    
    #get rgb based on directional components
    directions_colors = orient2rgb(directions)
    
    return centers,directions,directions_colors,heights

def plot_directions(peak_dirs,peak_values,x_angle,y_angle,fname,size=(300,300)):
    """
    Opens a 3-d fury window of the maximum peaks visualized
    
    To show a slice, provide a sliced volume of the peak_dirs and peak_values and adjust the x_angle and y_angle 
    See Tractography Directional Field QA Tutorial for examples
    
    Parameters
    -----------
    peak_dirs: np array of peak_dirs 
    peak_values: np array of peak_values
    slices: dictionary of lists of slices in x,y,z plane
    x_angle: angle to rotate image along x axis
    y_angle: angle to rotate image along y axis
    fname: str path to save
    size: size tuple for each image
    """    
    centers,directions,directions_colors,heights = generate_3_d_directions(peak_dirs,peak_values)
    
    scene = window.Scene()
    arrow_actor = actor.arrow(centers, directions, directions_colors, heights)

    scene.add(arrow_actor)
    scene.roll(x_angle)
    scene.pitch(y_angle)
    
    window.show(scene, size = size)

def create_qa_figure(peak_dirs,peak_values,output_dir,model):
    """
    Creates a 9x9 figure of the 3-d volume and saves it
    
    Parameters
    -----------
    peak_dirs: np array of peak_dirs 
    peak_values: np array of peak_values
    output_dir: location to save qa figure
    model: model type (CSA, CSD)
    """
    #title
    title = f'QA for Tractography {model} Model Peak Directions'
    
    #set shape of image
    im_shape = peak_dirs.shape[0:3]
    im_shape_rgb = im_shape + (3,)
    
    #generate 3-d directional data
    centers,directions,directions_colors,heights = generate_3_d_directions(peak_dirs,peak_values)
    
    #reshape back into a 3-d volume with voxel encoded RGB values corresponding to directional vectors
    im = directions_colors.reshape(im_shape_rgb)
    
    x = [int(im_shape[0] * 0.35), int(im_shape[0] * 0.51), int(im_shape[0] * 0.65)]
    y = [int(im_shape[1] * 0.35), int(im_shape[1] * 0.51), int(im_shape[1] * 0.65)]
    z = [int(im_shape[2] * 0.35), int(im_shape[2] * 0.51), int(im_shape[2] * 0.65)]
    coords = (x, y, z)
    labs = [
        "Sagittal Slice (YZ fixed)",
        "Coronal Slice (XZ fixed)",
        "Axial Slice (XY fixed)",
    ]
    var = ["X", "Y", "Z"]
    
    idx = 0
    for i, coord in enumerate(coords):
        for pos in coord:
            idx += 1
            ax = plt.subplot(3, 3, idx)
            ax.set_title(var[i] + " = " + str(pos))
            if i == 0:
                image = ndimage.rotate(im[pos, :, : , :], 90)
            elif i == 1:
                image = ndimage.rotate(im[:, pos, : , :], 90)
            else:
                image = im[:, :, pos, :]

            if idx % 3 == 1:
                ax.set_ylabel(labs[i])
                ax.yaxis.set_ticks([0, image.shape[0] / 2, image.shape[0] - 1])
                ax.xaxis.set_ticks([0, image.shape[1] / 2, image.shape[1] - 1])
            #casting to deal with clipping issue in matplotlib
            plt.imshow((image * 255).astype(np.uint8))
            
    fig = plt.gcf()
    fig.suptitle(title)
    fig.set_size_inches(12.5, 10.5, forward=True)
    fig.savefig(output_dir)
