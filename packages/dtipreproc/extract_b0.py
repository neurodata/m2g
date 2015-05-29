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


def extract_vol(dti_img, b0, b0_vol):
	"""
	Extracts and saves the B0 volume from a DTI volume stack.
	
	When performing DTI registration, eddy correction, and multi-modal registration, the B0 scan of a DTI volume is often needed. Given the set of b-values used by the scanner and the DTI volume set, we can extract the B0 volume and save it as a niftii image for easier access in further processing.
	
	**Positional Arguments**
	
			DTI Image: [nifti]
					- Original DTI volume stack from scanner
			B0 Index: [int] (default = 0)
					- Location of b=0 volume in the DTI stack
	
	**Returns**
	
			B0 Volume: [nifti]
					- Output volume containing the DTI volume corresponding to a b0 index
	"""
	print "Loading dti data..."
	d_img = load(dti_img)
	b0_data = d_img.get_data()
	b0_head = d_img.get_header()
  
	print "Extracting B0 volume..."
	b0_data=b0_data[:,:,:,b0]
	
	print "Updating image header..."
	b0_head.set_data_shape(b0_head.get_data_shape()[0:3])

	print "Saving..."
	out = Nifti1Image( b0_data, affine=d_img.get_affine(), header=b0_head )
	out.update_header()
	save(out, b0_vol)
	print "Complete!"

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("dti", action="store", help="The DTI image we want to extract B0 from (.nii, .nii.gz)")
  parser.add_argument("b0", action="store", help="The index of the b-value corresponding to the B0 scan")
  parser.add_argument("b0_vol", action="store", help="The output file location of the B0 scan (.nii, .nii.gz)")

  result = parser.parse_args()

  extract_vol(result.dti, result.b0, result.b0_vol)
  
if __name__ == "__main__":
    main()
    
