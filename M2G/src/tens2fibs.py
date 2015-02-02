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

# tens2fibs.py
# Created by Greg Kiar on 2015-01-09.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import string
import sys
import re
import os
from os.path import basename

def make_fibs(tensors, mask, anis, curve, fibers, vtk):
  [root, ext] = os.path.splitext(basename(fibers))

  # Perfoms fiber tractography in voxelspace on the given tensors
  os.system('track -inputmodel dt -seedfile '+mask+' -anisthresh '+anis+' -curvethresh '+curve+' -inputfile '+tensors+' > '+fibers+' -outputinvoxelspace 2>/cis/project/migraine/data/KKI2009/log/'+root+'_err.error')

  # Converts the fibers to an easy-to-view format
  os.system('vtkstreamlines -colourorient < '+fibers+' > '+vtk)


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("tensors", action="store", help="The tensors produced from the DTI image (.Bdouble)")
  parser.add_argument("mask", action="store", help="The brain mask of DTI image (.nii, .nii.gz)")
  parser.add_argument("anis", action="store", help="The anisotropic threshold value (default =0.2)")
  parser.add_argument("curve", action="store", help="The curvature threshold value (default =60)") 
  parser.add_argument("fibers", action="store", help="The produced fiber tracts (.Bfloat)")
  parser.add_argument("vtk", action="store", help="The fibers in another format (.vtk)")
  
  result = parser.parse_args()

  make_fibs(result.tensors, result.mask, result.anis, result.curve, result.fibers, result.vtk)


if __name__ == "__main__":
  main()
