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
    """
    fibs = np.load(fibfile)
    fibs = fibs[fibs.keys()[0]]
    fibs = threshold_fibers(fibs)
    # make sure if fiber streamlines
    # have no fibers, no error occurs
    if len(fibs) == 0: return
    resampled_fibs = random_sample(fibs, num_samples)
    
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
    if fname == None:
        fname = os.path.split(fibfile)[1].split('.')[0] + '.png'
    window.record(renderer, out_path=outdir + fname, size=(600, 600))
    print('done')   

def threshold_fibers(fibs):
    fib_lengths = [len(f) for f in fibs]
    if (len(fib_lengths) == 0): return fib_lengths
    med = np.median(fib_lengths)
    maximum = max(fib_lengths)
    minimum = min(fib_lengths)
    long_fibs = [f for f in fibs if len(f) > med]
    return long_fibs

def random_sample(fibs, num_samples):
    if (len(fibs) <= num_samples): num_samples = len(fibs)
    samples = random.sample(range(len(fibs)), num_samples)
    return [fibs[i] for i in samples]

def load_atlas(path, opacity):
    nifti_reader = vtk.vtkNIFTIImageReader()
    nifti_reader.SetFileName(path)
    nifti_reader.Update()

    # The following class is used to store transparencyv-values for later retrival. In our case, we want the value 0 to be
    # completly opaque whereas the three different cubes are given different transperancy-values to show how it works.
    alphaChannelFunc = vtk.vtkPiecewiseFunction()
    alphaChannelFunc.AddPoint(0, 0.0)
    print(opacity)
    alphaChannelFunc.AddPoint(1, opacity)

    # This class stores color data and can create color tables from a few color points. For this demo, we want the three cubes
    # to be of the colors red green and blue.
    colorFunc = vtk.vtkColorTransferFunction()
    colorFunc.AddRGBPoint(0, 0.0, 0.0, 0.0)
    colorFunc.AddRGBPoint(1, 1.0, 1.0, 1.0)

    # The preavius two classes stored properties. Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(alphaChannelFunc)
    volumeProperty.ShadeOn()


    # This class describes how the volume is rendered (through ray tracing).
    # compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    # We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkSmartVolumeMapper()
    # volumeMapper.SetBlendModeToComposite()
    volumeMapper.SetInputDataObject(nifti_reader.GetOutput())

    # The class vtkVolume is used to pair the preaviusly declared volume as well as the properties to be used when rendering that volume.
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
    parser = ArgumentParser(description="Generates a fiber png based on fibers and atlas")
    parser.add_argument("fibfile", action="store", help="base directory loc")
    parser.add_argument("atlasfile", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    parser.add_argument("--opacity", action="store", help="opacity of overlayed atlas file", type=float, default=0.05)
    parser.add_argument("--samples", action="store", help="change number of fibers to show in png", type=int, default=4000)
    result = parser.parse_args()

    visualize(result.fibfile, result.atlasfile, result.outdir, result.opacity, result.samples)

if __name__ == "__main__":
    main()
