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
compDir = params[3]
outputMatch2 = params[4]

print outputDir
print compDir
print outputMatch

# Generate Header List
headerList = list()

headerList.append(' ')
headerList.append('Total Count New')
headerList.append('Total Count Original')
headerList.append('Total Difference')
headerList.append('Total Absolute Difference')
headerList.append('Total Percent Difference')
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
for root, dirnames, filenames in os.walk(compDir):	
	for filename in fnmatch.filter(filenames, '*'+outputMatch2):
		mat1file = os.path.join(root,filename)
		dir2.append(mat1file)
dir2 = sorted(dir2)
print dir2

# Original Output Iterator
icompList = iter(dir2)

# Generate Label List
labelList = list()

for item in os.listdir(outputDir):
	if os.path.isdir(os.path.join(outputDir,item)):
		labelList.append(item)
labelList = sorted(labelList)
print labelList

# List Iterator
iLabelList = iter(labelList)

with open((outputDir+'analysis_compare'+datetime.datetime.now().strftime("%Y%m%dT%H%M%S")+'.csv'), 'wb') as csvfile:
	rowwriter = csv.writer(csvfile, delimiter=',')
	rowwriter.writerow(headerList)

	for mat1file in dir1:
		
		nextRow = list()

		mat1file = sio.loadmat(mat1file)
		mat1 = mat1file['fibergraph']
		mat1 = mat1.todense()
		#print mat1

		mat2file = sio.loadmat(icompList.next())
		mat2 = mat2file['fibergraph']
		mat2 = mat2.todense()
		#mat2 = genfromtxt(icompList.next(), delimiter=' ')
		#mat2 = np.delete(mat2,0,1)
		#mat2 = np.delete(mat2,0,0)
		#mat2[np.isnan(mat2)]=0
		#print mat2

		# Print Out Results
		nextRow.append(iLabelList.next())

		matSumNew = mat1.sum()
		nextRow.append(matSumNew)
		
		matSumOld = mat2.sum()
		nextRow.append(matSumOld)
		
		matDiff = mat1.sum() - mat2.sum()
		nextRow.append(matDiff)

		matTotDiff = (np.absolute(mat1 - mat2)).sum()
		nextRow.append(matTotDiff)

		matTotPercDiff = (matSumNew - matSumOld)/((matSumNew + matSumOld)/2)
		matTotPercDiff = (ceil(matTotPercDiff * 100000)/100000)*100
		nextRow.append(matTotPercDiff)
		
		rowwriter.writerow(nextRow)	


print "VALIDATION COMPLETE"
