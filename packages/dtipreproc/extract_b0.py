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
# Created by Greg Kiar on 2015-02-21.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from argparse import ArgumentParser
from nibabel import load, save, Nifti1Image
from numpy import where, loadtxt

def extract_vol(dti_img, bvals, b0_vol):
	print "Loading dti data..."
	d_img = load(dti_img)
	b0_data = d_img.get_data()
	b0_head = d_img.get_header()
  
	print "Loading bvals file..."
	b = loadtxt(bvals)
	 
	b = int(where(b==0)[0])
	print "B0 Index: ((",b, "##"
	
	print "Extracting B0 volume..."
	b0_data=b0_data[:,:,:,b]
	
	print "Updating image header..."
	b0_head.set_data_shape(b0_head.get_data_shape()[0:3])

	print "Saving..."
	out = Nifti1Image( data=b0_data, affine=d_img.get_affine(), header=b0_head )
	out.update_header()
	save(out, b0_vol)
	print "Complete!"

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("dti", action="store", help="The DTI image we want to extract B0 from (.nii, .nii.gz)")
  parser.add_argument("bvals", action="store", help="The b-value file corresponding to the DTI image (.b)")
  parser.add_argument("b0", action="store", help="The output file location of the B0 scan (.nii, .nii.gz)")

  result = parser.parse_args()

  extract_vol(result.dti, result.bvals, result.b0)
  
if __name__ == "__main__":
    main()
    
