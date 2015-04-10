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

for root, dirnames, filenames in os.walk(inputDir):	
	for filename in filenames:

		matOrig = os.path.join(root,filename)

		filename, fileExtension = os.path.splitext(filename)

		if (fileExtension == '.grad' and "_old" in filename) or (fileExtension == '.b' and "_old" in filename):
		
			filename = filename.split("_")[0]+fileExtension
			print filename

			matfile = os.path.join(root,filename)
			print matfile
		
			print matOrig
			a=np.genfromtxt(matOrig, delimiter=' ')
			print a
			print a.shape
	
			b=np.matrix(a).transpose()
			print b
			print b.shape

			b[np.isnan(b)] = 0
	
			np.savetxt(matfile,b)
	
			os.remove(matOrig)
