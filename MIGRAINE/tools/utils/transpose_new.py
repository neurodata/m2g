#!/usr/bin/python

## Make a directory based on input parent directory and desired directory name ##
## mkDir(parentDir, dirName)

############################################################################################
## (c) 2012 The Johns Hopkins University / Applied Physics Laboratory.  All Rights Reserved.
## Proprietary Until Publicly Released
############################################################################################

from sys import argv
import string
import datetime
import os
import csv
import fnmatch
import shutil
import tarfile
import numpy as np

# read in command line args
params = list(argv)

input_dir = params[1]
file_match = params[2]
rows = int(params[3])
cols = int(params[4])
new_ext = params[5]

print input_dir
print file_match

total = 0

for root, dirnames, fnames in os.walk(input_dir):	
	for filename in fnmatch.filter(fnames, file_match):
		target_file = os.path.join(root, filename)

		target_data = np.loadtxt(target_file, delimiter=" ").reshape(rows, cols)
		
		print target_data.size

		total = total+1

		filetitle, fileExtension = os.path.splitext(filename)

		output_file = os.path.join(root,filetitle + new_ext)

		print output_file

		np.savetxt(output_file, target_data, delimiter=" ")

		os.remove(target_file)

print total
		


