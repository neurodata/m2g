#!/usr/bin/python

# tens2fibs.py
# Tensors produced from DTI data are tracked into fibers
# Version 0.1, G. Kiar, 01/09/2015

# Load necessary packages
from sys import argv
import string
import sys
import re
import os

# Pull necessary parameters
params = list(argv)
dti_tensors = params[1] # The tensors produced from the DTI image (.Bdouble)
dti_mask = params[2] # The brain mask of the DTI image (.nii, .nii.gz)
anis = params[3] # Anisotropic voxel threshold value (default 0.2) (val)
curve = params[4] # Curvature threshold (default 60) (val)

dti_fibers = params[5] # Produced fiber tracts (.Bfloat)(output)
vtk_fibers = params[6] # Converted fibers in visualizable format (.vtk)(output)


# Perfoms fiber tractography in voxelspace on the given tensors
os.system('track -inputmodel dt -seedfile '+dti_mask+' -anisthresh '+anis+' -curvethresh '+curve+' -inputfile '+dti_tensors+' > '+dti_fibers+' -outputinvoxelspace 2>/home/gkiar/vbox/stderrorlog.txt')

# Converts the fibers to an easy-to-view format
os.system('vtkstreamlines -colourorient < '+dti_fibers+' > '+vtk_fibers)
