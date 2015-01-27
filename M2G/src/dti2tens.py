#!/usr/bin/python

# dti2tens.py
# DTI images are converted to tensor images
# Version 0.1, G. Kiar, 01/09/2015

# Load necessary packages
from sys import argv
import string
import sys
import re
import os

# Pull necessary parameters
params = list(argv)
dti_image = params[1] # The DTI image (skull stripped or not? idc) (.nii, .nii.gz)
dti_grad = params[2] # The gradient directions corresponding to the DTI image (.grad)
bval = params[3] # The bvalue corresponding to the DTI image  (default 700) (val)
dti_mask = params[4] # The brain mask of the DTI image (which is why I don't care if skull stripped original) (.nii, .nii.gz)

dti_scheme = params[5] # The scheme file (.scheme)(output)
dti_bfloat = params[6] # The Bfloat format equivalent of the DTI image (.Bfloat)(output)
dti_tensors = params[7] # The produced tensors in Bdouble format (.Bdouble)(output)
fa = params[8] # The fractional anisotropy statistic (.nii)(output)
md = params[9] # The mean diffusivity statistic (.nii)(output)
dti_eigs = params[10] # The eigen values of the system (.Bdouble)(output)

print dti_image
print dti_grad
print bval
print dti_mask
print dti_scheme
print dti_bfloat
print dti_tensors
print fa
print md
print dti_eigs


# Create scheme file
print 'pointset2scheme -inputfile '+dti_grad+' -bvalue '+bval+' -outputfile '+dti_scheme
os.system('pointset2scheme -inputfile '+dti_grad+' -bvalue '+bval+' -outputfile '+dti_scheme)


# Maps the DTI image to a Camino compatible Bfloat format
print 'image2voxel -4dimage '+dti_image+' -outputfile '+dti_bfloat
os.system('image2voxel -4dimage '+dti_image+' -outputfile '+dti_bfloat)

# Produce tensors from image
print 'dtfit '+dti_bfloat+' '+dti_scheme+' -bgmask '+dti_mask+' -outputfile '+dti_tensors
os.system('dtfit '+dti_bfloat+' '+dti_scheme+' -bgmask '+dti_mask+' -outputfile '+dti_tensors)

# In order to visualize, and just 'cause it's fun anyways, we get some stats
print 'for PROG in fa md; do cat '+dti_tensors+' | ${PROG} | voxel2image -outputroot ${PROG} -header '+dti_image+'; done'
os.system('for PROG in '+fa+' '+md+'; do cat '+dti_tensors+' | ${PROG} | voxel2image -outputroot ${PROG} -header '+dti_image+'; done')
os.system('mv fa.nii '+fa)
os.system('mv md.nii '+md)

# We also need the eigen system to visualize
print 'cat '+dti_tensors+' | dteig > '+dti_eigs
os.system('cat '+dti_tensors+' | dteig > '+dti_eigs)