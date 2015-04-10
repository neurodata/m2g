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

# register_affine.py
# Created by Greg Kiar on 2015-02-26.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

# Load necessary packages
from os import system
from argparse import ArgumentParser


def do_registration(fixed, moving, tol, out, rig):
    
    # Apply affine transformation
    system('antsRegistration -d 3 -o [r,'+out+'] -r ['+fixed+', '+moving+',1] -m Mattes[ '+fixed+', '+moving+',1,12] -t Rigid[0.75] -c [25, '+tol+', 5] --smoothing-sigmas 1 -f 1')
    system('cp r0GenericAffine.mat '+ rig)


def main():
  parser = ArgumentParser(description="")
  parser.add_argument("fixed", action="store", help="Image that we are registering to (.nii, .nii.gz)")
  parser.add_argument("moving", action="store", help="Image that we are transforming (.nii, .nii.gz)")
  parser.add_argument("tol", action="store", help="Error tolerance value (default 1e-4)")
  parser.add_argument("out", action="store", help="The transformed output image (.nii, .nii.gz)") 
  parser.add_argument("rig", action="store", help="Affine transform matrix output (.mat)")
  
  result = parser.parse_args()

  do_registration(result.fixed, result.moving, result.tol, result.out, result.rig)


if __name__ == "__main__":
  main()
