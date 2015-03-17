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
  print "Loading data..."
  d_img = load(data_img)
  d_data = d_img.get_data()
  
  print "Loading mask..."
  m_img = load(mask)
  m_img.get_header().set_data_shape(m_img.get_header().get_data_shape()[0:3])
  m_data = m_img.get_data()
  
  print "Determining data dimensions..."
  t = d_img.get_header()
  t = t.get_data_shape()
  dimension = len(t)
  
  #assumes that mask dimension is 3d
  i,j,k= where(m_data[0:2] == 0)
  if dimension == 3:
    print "Masking 3D Image..."
    d_data[i,j,k] = 0
  elif dimension == 4:
    print "Masking 4D Image..."
    for q in range(t[3]):
      print "Applying mask to layer", q+1, " of ", t[3]
      d_data[i,j,k,q] = 0
  print "Masking complete!"
  
  print "Saving..."
  out = Nifti1Image( data=d_data, affine=d_img.get_affine(), header=d_img.get_header() )
  save(out, output_img)
  print "Complete!"


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("data", action="store", help="The image we want to mask (.nii, .nii.gz)")
  parser.add_argument("mask", action="store", help="The binary mask (.nii, .nii.gz)")
  parser.add_argument("output", action="store", help="masked output image (.nii, .nii.gz)")

  result = parser.parse_args()

  masking(result.data, result.mask, result.output)
  
if __name__ == "__main__":
    main()
    
