#!/usr/bin/env python

# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

# regi.py
# Created by Greg Kiar on 2015-01-09.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

# Load necessary packages
import argparse
import string
import sys
import re
import os
from os.path import basename


def do_registration(fixed, moving, tol, out, tra, rig, aff):
    [root, ext] = os.path.splitext(basename(out))
    
    intermediate = 'temp.nii'
    # Apply translation transformation
    os.system('antsRegistration -d 3 -o [t,'+intermediate+'] -r ['+fixed+', '+moving+',1] -m Mattes[ '+fixed+', '+moving+',1,12] -t Translation[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
    os.system('mv t0GenericAffine.mat '+ tra)

    # Apply rigid transformation
    os.system('antsRegistration -d 3 -o [r,'+intermediate+'] -r ['+fixed+', '+intermediate+',1] -m Mattes[ '+fixed+', '+intermediate+',1,12] -t Rigid[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
    os.system('mv r0GenericAffine.mat '+ rig)
    
    # Apply affine transformation
    os.system('antsRegistration -d 3 -o [a,'+out+'] -r ['+fixed+', '+intermediate+',1] -m Mattes[ '+fixed+', '+intermediate+',1,12] -t Affine[0.75] -c [100x75x50x25, '+tol+', 5] --smoothing-sigmas 9x5x3x1 -f 4x3x2x1')
    os.system('mv a0GenericAffine.mat '+ aff)
    os.system('rm '+intermediate)


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("fixed", action="store", help="Image that we are registering to (.nii, .nii.gz)")
  parser.add_argument("moving", action="store", help="Image that we are transforming (.nii, .nii.gz)")
  parser.add_argument("tol", action="store", help="Error tolerance value (default 1e-4)")
  parser.add_argument("out", action="store", help="The transformed output image (.nii, .nii.gz)") 
  parser.add_argument("tra", action="store", help="Translation transform matrix output (.mat)")
  parser.add_argument("rig", action="store", help="Rigid transform matrix output (.mat)")
  parser.add_argument("aff", action="store", help="Affine transform matrix output (.mat)")
  
  result = parser.parse_args()

  do_registration(result.fixed, result.moving, result.tol, result.out, result.tra, result.rig, result.aff)


if __name__ == "__main__":
  main()
