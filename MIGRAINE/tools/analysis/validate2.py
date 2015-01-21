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
from os.path import join
import csv
from math import ceil
import scipy.io as sio

# read in command line args
params = list(argv)

newDir = params[1]
oldDir = params[2]
outputDir = params[3]
newMatch = params[4]
oldMatch = params[5]

newFiles = list()
oldFiles = list()

for root, dirs, files in os.walk(newDir):
	for name in files:	
		if name.endswith(newMatch):
			
			newF = join(root,name)
			
			newFiles.append(newF)

for root, dirs, files in os.walk(oldDir):
	for name in files:	
		if name.endswith(oldMatch):
			
			oldF = join(root,name)
			
			oldFiles.append(oldF)
newFiles.sort()
oldFiles.sort()

print newFiles
print oldFiles

iOld = iter(oldFiles)

resultArray = np.zeros([70,70])

#counter = 0

with open((outputDir+'analysis'+datetime.datetime.now().strftime("%Y%m%dT%H%M%S")+'.csv'), 'wb') as csvfile:
	rowwriter = csv.writer(csvfile, delimiter=',')
	
	headerrow = list()
	headerrow.extend(['Subject','Total Fibers','Total Absolute Error','Total Error'])
	rowwriter.writerow(headerrow)

	for new_file in newFiles:

		print new_file
		old_file = iOld.next()
	
		newD = sio.loadmat(new_file)
		
		print newD

		newD = newD['fibergraph']
		newD = newD.todense()


		print newD
		
		#newD = np.delete(newD,0,1)
		#newD = np.delete(newD,0,0)

		oldD = genfromtxt(old_file, delimiter=' ')
		oldD = np.delete(oldD,0,1)
		oldD = np.delete(oldD,0,0)

		diff = np.subtract(newD,oldD)

		absdiff = np.absolute(diff)

		result = np.divide(absdiff,oldD)
	
		resultArray = np.add(diff, resultArray)

		#np.savetxt((outputDir + "analysis" + str(counter) + ".csv"), result, delimiter=",")
		#counter = counter + 1

		tempRow = list()

		subject = os.path.realpath(new_file)

		subject = subject[(subject.rfind('/')+1):]
		subject = subject[:10]
		tempRow.append(subject)

		totalSum = newD.sum()
		errorSum = diff.sum()
		absErrorSum = absdiff.sum()

		tempRow.append(totalSum)
		tempRow.append(absErrorSum)
		tempRow.append(errorSum)

		rowwriter.writerow(tempRow)
		break


resultArray = np.nan_to_num(resultArray)
resultArray = np.divide(resultArray,42)

np.savetxt((outputDir + "analysis.csv"), resultArray, delimiter=",")



			
