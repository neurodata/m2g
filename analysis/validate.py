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
for root, dirnames, filenames in os.walk(compDir):	
	for filename in fnmatch.filter(filenames, '*'+outputMatch2):
		mat1file = os.path.join(root,filename)
		dir2.append(mat1file)
dir2 = sorted(dir2)
print dir2

# Original Output Iterator
icompList = iter(dir2)


print "VALIDATION COMPLETE"
