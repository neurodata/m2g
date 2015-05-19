#!/usr/bin/python

## Make a directory based on input parent directory and desired directory name ##
## mkDir(parentDir, dirName)

############################################################################################
## (c) 2012 The Johns Hopkins University / Applied Physics Laboratory.  All Rights Reserved.
## Proprietary Until Publicly Released
############################################################################################

from numpy import linalg as LA
from numpy import genfromtxt
import numpy as np
from sys import argv
import string
import datetime
import os
import csv
import fnmatch
from math import ceil
import scipy.io as sio

# read in command line args
params = list(argv)

outputDir = params[1]
outputMatch = params[2]

print outputDir
print outputMatch

# Generate Header List
headerList = list()

for item in os.listdir(outputDir):
	if os.path.isdir(os.path.join(outputDir,item)):
		headerList.append(item)
headerList = sorted(headerList)
headerList.insert(0,' ')
print headerList

# Generate dir1 List
dir1 = list()	
for root, dirnames, filenames in os.walk(outputDir):	
	for filename in fnmatch.filter(filenames, '*'+outputMatch):
		mat1file = os.path.join(root,filename)
		dir1.append(mat1file)
dir1 = sorted(dir1)
print dir1

# Generate dir2 List
dir2 = list()	
for root, dirnames, filenames in os.walk(outputDir):	
	for filename in fnmatch.filter(filenames, '*'+outputMatch):
		mat1file = os.path.join(root,filename)
		dir2.append(mat1file)
dir2 = sorted(dir2)
print dir2

# List Iterator
iHeaderList = iter(headerList)
print iHeaderList.next()

with open((outputDir+'analysis_test_retest'+datetime.datetime.now().strftime("%Y%m%dT%H%M%S")+'.csv'), 'wb') as csvfile:
	rowwriter = csv.writer(csvfile, delimiter=',')
	rowwriter.writerow(headerList)

	for mat1file in dir1:
		
		nextRow = list()
		nextRow.append(iHeaderList.next())

		mat1file = sio.loadmat(mat1file, squeeze_me=False, struct_as_record=False)
		mat1 = mat1file['fibergraph']
		matl1 = np.zeros((70,70))
		matc1 = mat1 + matl1
		print matc1

		for mat2file in dir2:

			mat2file = sio.loadmat(mat2file, squeeze_me=False, struct_as_record=False)
			mat2 = mat2file['fibergraph']
			matl2 = np.zeros((70,70))
			matc2 = mat2 + matl2
			print matc2

			matDiff = np.subtract(matc1,matc2)
			matFroNorm = LA.norm(matDiff,'fro')
			
			nextRow.append(matFroNorm)
		
		rowwriter.writerow(nextRow)	

print "VALIDATION COMPLETE"
