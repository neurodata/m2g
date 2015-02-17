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

# mask_nifti.py
# Created by Greg Kiar on 2015-02-17.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
from nibabel import load, save, Nifti1Image
from numpy import where

def masking(data_img, mask, output_img):
  d_img = load(data_img)
  d_data = d_img.get_data()
  
  m_img = load(mask)
  m_data = m_img.get_data()

  i,j,k= where(m_data == 0)
  d_data[i,j,k] = 0

  out = Nifti1Image( data=d_data, affine=d_img.get_affine(), header=d_img.get_header() )
  save(out, output_img)


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("data", action="store", help="The image we want to mask (.nii, .nii.gz)")
  parser.add_argument("mask", action="store", help="The binary mask (.nii, .nii.gz)")
  parser.add_argument("output", action="store", help="masked output image (.nii, .nii.gz)")
  result = parser.parse_args()

  masking(result.data, result.mask, result.output)
  
if __name__ == "__main__":
    main()
    