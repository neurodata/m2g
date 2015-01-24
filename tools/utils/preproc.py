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

# make subject directories
for root, dirnames, filenames in os.walk(inputDir):	
	for filename in fnmatch.filter(filenames, '*'+inputMatchMPRAGE+'*'):
		filename, fileExtension = os.path.splitext(filename)

		foldername = filename.split(inputMatchMPRAGE)[1].split("s")[0]
		
		folder = os.path.join(inputDir,foldername)

		print folder
		
		if not os.path.exists(folder):
			os.makedirs(folder)

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

			dirname = filename.split(inputMatchDTI)[1].split("s")[0]

			newname = string.replace(dirname,inputMatchBVAL,'')
			newname = string.replace(newname,'MPRAGE','')
			newname = string.replace(newname,'DTI','')
			dst = os.path.join(inputDir,dirname)
			dst = os.path.join(dst,newname+'_old.b')
			print dst

			os.rename(src,dst)

		if inputMatchBVEC in fileExtension:
			src = os.path.join(root,filename+fileExtension)
			print src

			dirname = filename.split(inputMatchDTI)[1].split("s")[0]

			newname = string.replace(dirname,inputMatchBVEC,'')
			newname = string.replace(newname,'MPRAGE','')
			newname = string.replace(newname,'DTI','')
			dst = os.path.join(inputDir,dirname)
			dst = os.path.join(dst, newname+'_old.grad')
			print dst

			os.rename(src,dst)

		if inputMatchMPRAGE in filename:
			src = os.path.join(root,filename+fileExtension)
			print src

			dirname = filename.split(inputMatchMPRAGE)[1].split("s")[0]

			newname = string.replace(dirname,inputMatchMPRAGE,'')
			newname = string.replace(newname,'MPRAGE','')
			newname = string.replace(newname,'DTI','')
			dst = os.path.join(inputDir,dirname)
			dst = os.path.join(dst, newname+'_MPRAGE'+fileExtension)
			print dst
					
			os.rename(src,dst)

		if inputMatchDTI in filename:
			if ".nii" == fileExtension:
				src = os.path.join(root,filename+fileExtension)
				print src
				print "DTI"

				dirname = filename.split(inputMatchDTI)[1].split("s")[0]

				newname = string.replace(dirname,inputMatchDTI,'')
				newname = string.replace(newname,'MPRAGE','')
				newname = string.replace(newname,'DTI','')
				dst = os.path.join(inputDir,dirname)
				dst = os.path.join(dst, newname+'_DTI'+fileExtension)
				print dst
					
				os.rename(src,dst)
