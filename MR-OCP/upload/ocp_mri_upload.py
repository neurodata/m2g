#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

# ocp_mri_upload.py
# Created by Greg Kiar on 2015-07-01.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser

def nifti_upload(infname, token):
	from nibabel import load
	from numpy import array

	print "Parsing nifti file..."
	nifti_img = load(infname)
	nifti_data = array(nifti_img.get_data())

	#RB TODO: upload data
	import pdb; pdb.set_trace()
	
def swc_upload(infname, token):
	from contextlib import closing

	print "Parsing skeleton file..."
	with closing(open(infname, mode="rb")) as fiber_f:
		fdata = fiber_f.read()
	lines = fdata.split("\n")
	count = 0
	for line in lines: #GK TODO: speed up; isn't huge deal because headers are short
		if line[0] == "#":
			count += 1
		else:
			break #this assumes no comments after header

	head = lines[:count]
	skel = lines[count:]

	#Displaying shit to happy users :)
	print "Header:"
	for elem in head:
		print elem
	if len(skel) <= 2:
		print "\nData: \n", skel[0], "\n..."
	else:
		print "\nData: \n", skel[0], "\n", skel[1], "\n..."

	#RB TODO: upload data
	import pdb; pdb.set_trace()

def main():
	parser = ArgumentParser(description="Allows users to upload nifti images to OCP")
	parser.add_argument("data", action="store", help="Data which is to be uploaded")
	parser.add_argument("token", action="store", help="token for the project which you're uploading to")
	parser.add_argument("--formats", "-f", action="store", default="nifti", help="format: nifti, swc")
	result = parser.parse_args()
	
	if result.formats == "nifti":
		nifti_upload(result.data, result.token)
	elif result.formats == "swc":
		swc_upload(result.data, result.token)
	else:
		print 'Error: unknown format'
		return -1

if __name__ == "__main__":
	main()
