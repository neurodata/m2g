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
from os.path import basename, dirname

def remove_skull(image, f, g, brain, mask):
  [root, ext1] = os.path.splitext(basename(brain))
  [root, ext2] = os.path.splitext(root)
  
  os.system('bet '+image+' '+brain+' -f '+f+' -g '+g+' -m')
  print dirname(brain)+root
  os.system('mv '+dirname(brain)+root+'_mask'+ext2+ext1+' '+mask)

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("image", action="store", help="The original brain scan (.nii, .nii.gz)")
  parser.add_argument("f", action="store", help="Fractional Intensity value (default=0.5)")
  parser.add_argument("g", action="store", help="Vertical Gradient value (default =0)")
  parser.add_argument("brain", action="store", help="The skull removed brain (.nii.gz)") 
  parser.add_argument("mask", action="store", help="The binarized brain mask (.nii.gz)")
  
  result = parser.parse_args()

  remove_skull(result.image, result.f, result.g, result.brain, result.mask)


if __name__ == "__main__":
    main()