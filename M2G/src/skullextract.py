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

# skullextract.py
# Created by Greg Kiar on 2015-01-09.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.


import argparse
import os
from os.path import basename

def remove_skull(image, f, g, brain, mask):
  [root, ext1] = os.path.splitext(basename(outf))
  [root, ext2] = os.path.splitext(root)
  
  os.system('bet '+image+' '+brain+' -f '+f+' -g '+g+' -m')

  os.system('mv '+root+'_mask'+ext2+ext1+' '+mask)

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("image", action="store", help="The tensors produced from the DTI image (.Bdouble)")
  parser.add_argument("f", action="store", help="The brain mask of DTI image (.nii, .nii.gz)")
  parser.add_argument("g", action="store", help="The anisotropic threshold value (default =0.2)")
  parser.add_argument("brain", action="store", help="The curvature threshold value (default =60)") 
  parser.add_argument("mask", action="store", help="The produced fiber tracts (.Bfloat)")
  
  result = parser.parse_args()

  remove_skull(result.image, result.f, result.g, result.brain, result.mask)


if __name__ == "__main__":
    main()