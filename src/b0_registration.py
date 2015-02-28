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

# extract_b0.py
# Created by Greg Kiar on 2015-02-23.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from argparse import ArgumentParser
from nibabel import load, save, Nifti1Image
from numpy import where, loadtxt
from os import system

def register_vol(dti_img, bvals, aligned_img, b0_img):
  print "Loading dti data..."
  dti_vol = load(dti_img)
  dti_data = dti_vol.get_data()
  
  print "Loading bvals file..."
  b = loadtxt(bvals)
  
  print "Extracting B0 volume..."
  b0_vol=dti_data[:,:,:,int(where(b==0)[0])]
  b0_head = dti_vol.get_header()
  b0_head.set_data_shape(b0_head.get_data_shape()[0:3])
  b0_out = Nifti1Image( data=b0_vol, affine=dti_vol.get_affine(), header=b0_head )
  save(b0_out, b0_img)
  
  directions = dti_vol.get_shape()[3]
  print "Number of 3D volumes:", directions
  
  aligned_vol = dti_vol
  aligned_data = aligned_vol.get_data()
  print "Beginning registration..."
  temp_in_img = 'temp_in.nii'
  temp_out_img = 'temp_out.nii'
  temp_head = dti_vol.get_header()
  temp_head.set_data_shape(temp_head.get_data_shape()[0:3])
  
  for ii in range(directions):
    print "Volume ", ii+1, " of ", directions
    if ii == int(where(b==0)[0]):
      print "Skipping self registration for B0 scan..."
      continue
    currentvol = aligned_data[:,:,:,ii]
    #print "Writing current volume to disk..."
    out = Nifti1Image( data=currentvol, affine=dti_vol.get_affine(), header=temp_head )
    save(out, temp_in_img)
    system('antsRegistration -d 3 -o [affine,'+temp_out_img+'] -r ['+b0_img+', '+temp_in_img+',1] -m Mattes[ '+b0_img+', '+temp_in_img+',1,12] -t Affine[0.75] -c [25, 1e-4, 5] --smoothing-sigmas 1 -f 1 > /dev/null')
    temp_vol = load(temp_out_img)
    currentvol = temp_vol.get_data()
    aligned_data[:,:,:,ii] = currentvol
    system('rm '+temp_out_img+';rm '+temp_in_img)
    
  system('rm  affine0GenericAffine.mat')
  
  dims = dti_vol.get_header().get_data_shape()
  dti_vol.get_header().set_data_shape((dims[0], dims[1], dims[2], directions))
  out = Nifti1Image( data=aligned_data, affine=dti_vol.get_affine(), header=dti_vol.get_header() )
  
  save(out, aligned_img)


def main():
  parser = ArgumentParser(description="")
  parser.add_argument("DTI", action="store", help="The DTI image we want to extract B0 from (.nii, .nii.gz)")
  parser.add_argument("bvals", action="store", help="The b-value file corresponding to the DTI image (.b)")
  parser.add_argument("alignedDTI", action="store", help="The output file location of the aligned DTI volume  scan (.nii, .nii.gz)")
  parser.add_argument("B0", action="store", help="The output file location of the B0 scan (.nii, .nii.gz)")
  result = parser.parse_args()

  register_vol(result.DTI, result.bvals, result.alignedDTI, result.B0)
  
if __name__ == "__main__":
    main()
    
