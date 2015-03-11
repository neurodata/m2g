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
import fnmatch
import numpy as np

# read in command line args
params = list(argv)

inputDir = params[1]
inputMatchDTI = params[2]
inputMatchMPRAGE = params[3]
inputMatchBVAL = params[4]
inputMatchBVEC = params[5]

# move files to directories
for root, dirnames, files in os.walk(inputDir):	
	for filename in files:
		filename, fileExtension = os.path.splitext(filename)
		print "NEW"		
		print filename
		print fileExtension

		if inputMatchBVAL in fileExtension:
			src = os.path.join(root,filename+fileExtension)
			print src

			dst = os.path.join(root,'bval.b')
			print dst

			os.rename(src,dst)

		if inputMatchBVEC in fileExtension:
			src = os.path.join(root,filename+fileExtension)
			print src

			dst = os.path.join(root,'bvec.grad')
			print dst

			os.rename(src,dst)

		if inputMatchMPRAGE in filename:
			src = os.path.join(root,filename+fileExtension)
			print src

			dst = os.path.join(root,'mprage_MPRAGE.nii.gz')
			print dst
					
			os.rename(src,dst)

		if inputMatchDTI in filename:
			if ".gz" == fileExtension:
				src = os.path.join(root,'dti.nii.gz')
				print src

				dst = os.path.join(root,'dti_DTI.nii.gz')
				print dst
					
				os.rename(src,dst)
