#!/usr/bin/python

# regi.py
# Registers an image to a template image
# Version 0.1, G. Kiar, 01/09/2015

# Load necessary packages
from sys import argv
import string
import sys
import re
import os

# Pull necessary parameters
params = list(argv)
img_fixed = params[1] # Image that we are registering to (.nii, .nii.gz)
img_moving = params[2] # Image that we are transforming (.nii, .nii.gz)
tol = params[3] # Error tolerance (default 1e-5) (val) 

img_out = params[4] # The transformed output image (.nii, .nii.gz)(output)
tran = params[5] # Translation transform matrix output (no ext)(output)  <-- For these, ANTs auto-populates the rest of the title and the extension... this ok?
rigi = params[6] # Rigid transform matrix output (no ext)(output)        <--
affi = params[7] # Affine transform matrix output (no ext)(output)       <--
#TODOGK: Implement nonl transform
#nonl = params[8] # Non-linear transform matrix output (no ext)(output)

[root, ext] = os.path.splitext(img_out)
tempname = 'temp'+ext
# Apply translation transformation
os.system('antsRegistration -d 3 -o [t,'+img_out+'] -r ['+img_fixed+', '+img_moving+',1] -m Mattes[ '+img_fixed+', '+img_moving+',1,12] -t Translation[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
os.system('cp '+img_out+' '+tempname)
os.system('mv t0GenericAffine.mat '+ tran)

# Apply rigid transformation
os.system('antsRegistration -d 3 -o [r,'+img_out+'] -r ['+img_fixed+', '+tempname+',1] -m Mattes[ '+img_fixed+', '+img_out+',1,12] -t Rigid[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
os.system('cp '+img_out+' '+tempname)
os.system('mv r0GenericAffine.mat '+ rigi)

# Apply affine transformation
os.system('antsRegistration -d 3 -o [a,'+img_out+'] -r ['+img_fixed+', '+tempname+',1] -m Mattes[ '+img_fixed+', '+img_out+',1,12] -t Affine[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
os.system('mv a0GenericAffine.mat '+ affi)
#TODOGK: Implement nonl transform
