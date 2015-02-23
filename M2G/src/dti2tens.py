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

# dti2tens.py
# Created by Greg Kiar on 2015-01-09.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

# Load necessary packages
from argparse import ArgumentParser
from os import system
from os.path import basename, splitext


def make_tens(dti, grad, bval, mask, scheme, dti_bfloat, tensors, fa, md, eigs):
  # Create scheme file
  system('pointset2scheme -inputfile '+grad+' -bvalue '+bval+' -outputfile '+scheme)
  
  # Maps the DTI image to a Camino compatible Bfloat format
  system('image2voxel -4dimage '+dti+' -outputfile '+dti_bfloat)
  
  # Produce tensors from image
  system('dtfit '+dti_bfloat+' '+scheme+' -bgmask '+mask+' -outputfile '+tensors)
  
  # In order to visualize, and just 'cause it's fun anyways, we get some stats

  [fa_base, ext] = splitext(basename(fa))
  [md_base, ext] = splitext(basename(md))
  system('for PROG in '+fa_base+' '+md_base+'; do cat '+tensors+' | ${PROG} | voxel2image -outputroot ${PROG} -header '+dti+'; done')
  system('mv '+basename(fa)+' '+fa)
  system('mv '+basename(md)+' '+md)

  # We also need the eigen system to visualize
  system('cat '+tensors+' | dteig > '+eigs)

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("dti", action="store", help="The DTI image, not skull stripped (.nii)")
  parser.add_argument("grad", action="store", help="The gradient directions corresponding to the DTI image (.grad)")
  parser.add_argument("bval", action="store", help="The bvalue corresponding to the DTI image  (default 700)")
  parser.add_argument("mask", action="store", help="The brain mask of the DTI image (.nii, .nii.gz)") 
  parser.add_argument("scheme", action="store", help="The scheme file (.scheme)")
  parser.add_argument("dti_bfloat", action="store", help="The Bfloat format equivalent of the DTI image (.Bfloat)")
  parser.add_argument("tensors", action="store", help="The produced tensors in Bdouble format (.Bdouble)")
  parser.add_argument("fa", action="store", help="The fractional anisotropy statistic (.nii)")
  parser.add_argument("md", action="store", help="The mean diffusivity statistic (.nii)")
  parser.add_argument("eigs", action="store", help="The eigen values of the system (.Bdouble)")

  result = parser.parse_args()

  make_tens(result.dti, result.grad, result.bval, result.mask, result.scheme, result.dti_bfloat, result.tensors, result.fa, result.md, result.eigs)


if __name__ == '__main__':
  main()
