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

# qa_fibers.py
# Created by Vikram Chandrashekhar.
# Email: Greg Kiar @ gkiar@jhu.edu

import numpy as np
import nibabel as nib
import random
import sys
import os
import re
import vtk
import paramiko
import getpass
import subprocess

from dipy.viz import window, actor
from argparse import ArgumentParser


def visualize(fibfile, atlasfile, outdir, opacity, num_samples, fname=None):
    """
    Takes fiber streamlines and visualizes them using DiPy
    Required Arguments:
        - fibfile: Path to fiber file
        - atlasfile: Path to atlas file
        - outdir: Path to output directory
        - opacity: Opacity of overlayed brain
        - num_samples: number of fibers to randomly sample from fibfile
    Optional Arguments:
        - fname: name of output file. default is None (fname based on input
          fibfile name)
    """
    # loading the fibers
    fibs = np.load(fibfile)
    fibs = fibs[fibs.keys()[0]]
    fibs = threshold_fibers(fibs)

    # make sure if fiber streamlines
    # have no fibers, no error occurs
    if len(fibs) == 0:
        return
    # randomly sample num_samples fibers from given fibers
    resampled_fibs = random_sample(fibs, num_samples)

    # load atlas file
    atlas_volume = load_atlas(atlasfile, opacity)

    # Initialize renderer
    renderer = window.Renderer()

    # Add streamlines as a DiPy viz object
    stream_actor = actor.line(fibs)

    # Set camera orientation properties
    # TODO: allow this as an argument
    renderer.set_camera()  # args are: position=(), focal_point=(), view_up=()

    # Add streamlines to viz session
    renderer.add(stream_actor)
    renderer.add(atlas_volume)

    # Display fibers
    # TODO: allow size of window as an argument
    # window.show(renderer, size=(600, 600), reset_camera=False)

    # Saves file, if you're into that sort of thing...
    if fname is None:
        fname = os.path.split(fibfile)[1].split('.')[0] + '.png'
    window.record(renderer, out_path=outdir + fname, size=(600, 600))
    print('done')


def threshold_fibers(fibs):
    '''
    fibs: fibers as 2D array (N,3)
    '''
    fib_lengths = [len(f) for f in fibs]
    if (len(fib_lengths) == 0):
        return fib_lengths
    # calculate median of  fiber lengths
    med = np.median(fib_lengths)
    # get only fibers above the median length
    long_fibs = [f for f in fibs if len(f) > med]
    return long_fibs


def random_sample(fibs, num_samples):
    '''
    fibs: fibers thresholded above median
    num_samples: number of fibers to sample from fibs
    '''
    # if the number of samples is more than amount
    # of fibers available, then make num_samples
    # equal number of fibers available
    if (len(fibs) <= num_samples):
        num_samples = len(fibs)
    # generate the random sample indices
    samples = random.sample(range(len(fibs)), num_samples)
    return [fibs[i] for i in samples]


def load_atlas(path, opacity):
    '''
    path: path to atlas file
    opacity: opacity of overlayed atlas brain
    '''
    nifti_reader = vtk.vtkNIFTIImageReader()
    nifti_reader.SetFileName(path)
    nifti_reader.Update()

    # The following class is used to store transparencyv-values for later
    # retrival. In our case, we want the value 0 to be completly opaque
    alphaChannelFunc = vtk.vtkPiecewiseFunction()
    alphaChannelFunc.AddPoint(0, 0.0)
    alphaChannelFunc.AddPoint(1, opacity)

    # This class stores color data and can create color tables from a few color
    # points. For this demo, we want the three cubes to be of the colors red
    # green and blue.
    colorFunc = vtk.vtkColorTransferFunction()
    colorFunc.AddRGBPoint(0, 0.0, 0.0, 0.0)
    colorFunc.AddRGBPoint(1, 1.0, 1.0, 1.0)

    # The preavius two classes stored properties. Because we want to apply
    # these properties to the volume we want to render, we have to store them
    # in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(alphaChannelFunc)
    volumeProperty.ShadeOn()

    # We can finally create our volume. We also have to specify the data for
    # it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkSmartVolumeMapper()
    volumeMapper.SetInputDataObject(nifti_reader.GetOutput())

    # The class vtkVolume is used to pair the preaviusly declared volume as
    # well as the properties to be used when rendering that volume.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    return volume


def main():
    """
    Argument parser. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.
    Required parameters:
        fibfile:
            - Path to tensor file
        atlasfile:
            - Path to regdti file
        opacity:
            - Opacity of overlayed atlas file
        outdir:
            - Path to fa png save location
    """
    parser = ArgumentParser(description="Generates a fiber png based on fibers"
                            " and atlas")
    parser.add_argument("fibfile", action="store", help="base directory loc")
    parser.add_argument("atlasfile", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    parser.add_argument("--opacity", action="store", help="opacity of"
                        " overlayed atlas file", type=float, default=0.05)
    parser.add_argument("--samples", action="store", help="change number of"
                        " fibers to show in png", type=int, default=4000)
    result = parser.parse_args()

    visualize(result.fibfile, result.atlasfile, result.outdir, result.opacity,
              result.samples)

if __name__ == "__main__":
    main()
