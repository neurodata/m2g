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

# b_format.py
# Created by Greg Kiar on 2015-05-07.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.



from argparse import ArgumentParser
from numpy import where, loadtxt, savetxt
from os import system

def read_bvals(b_in):
	"""
	Parses b-values files provided by the scanner.
	
	The b-values received from the scanner indicate both the field intensity during the DTI scanning process as well as the index of the B0 volume. This function identifies both of these values.
	
	**Positional Arguments**
	
			B-values: [ASCII]
					- Ordered list of b-values from the scanner
	"""
	b = loadtxt(b_in)
	b0 = int(where(b==0)[0][0])
	bvalue = int(b[where(b!=0)[0][0]])
	
	system("echo 'b0=("+str(b0)+")'")
	system("echo 'bvalue=("+str(bvalue)+")'")

def format_bvec(b_in, b_out):	
	"""
	Parses b-vectors (or, gradient direction)  provided by the scanner.
	
	B-vectors can be provided in slightly different formats from different scanners, and this module parses them to ensure that downstream functions correctly perceive the information provided.
	
	**Positional Arguments**
	
			B-vectors: [ASCII]
					- Gradient directions of scanner corresponding to the b-values
			Gradients: [ASCII]
					- Reformatted B-vectors file which is compatible with downstream processing algorithms
	"""
	b = loadtxt(b_in)
	if b.shape[0] < b.shape[1]:
		b = b.T
	savetxt(b_out, b,  fmt='%.18f')

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("bval", action="store", help="The b-value file corresponding to the DTI image (.bval, .b)")
  parser.add_argument("bvec", action="store", help="The b-vector/gradient file corresponding to the DTI image (.bvec, .grad)")
  parser.add_argument("new_bvec", action="store", help="The new b-vector/gradient file (.grad)")

  result = parser.parse_args()
  read_bvals(result.bval)
  format_bvec(result.bvec, result.new_bvec)

if __name__ == "__main__":
    main()
