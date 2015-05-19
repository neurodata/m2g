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
from math import ceil

# read in command line args
params = list(argv)

outputDir = params[1]
compDir = params[2]
outputMatch = params[3]

print outputDir
print compDir
print outputMatch

headerList = list()
headerList.append(' ')

for root, subDirs, files in os.walk(compDir):
	for fileH in files:
		print fileH
		if fileH.endswith(outputMatch):
			subjectF = os.path.realpath(fileH)
			subjectF = subjectF[(subjectF.rfind('/')+1):]
			subject = subjectF[:10]
			headerList.append(subject)
print headerList
		
print "made it here"

with open((outputDir+'analysis'+datetime.datetime.now().strftime("%Y%m%dT%H%M%S")+'.csv'), 'wb') as csvfile:
	rowwriter = csv.writer(csvfile, delimiter=',')
	rowwriter.writerow(headerList)

	for files in oFileDir:
		if files.endswith(outputMatch):
			os.chdir(outputDir)

			tempRow = list()

			subjectF = os.path.realpath(files)

			print subjectF

			subject = subjectF[(subjectF.rfind('/')+1):]
			subject = subject[:10]
			tempRow.append(subject)

			print files

			initialD = genfromtxt(subjectF, delimiter=' ')
			initialD = np.delete(initialD,0,1)
			initialD = np.delete(initialD,-1,0)

			
			os.chdir(compDir)
			cFileDir = os.listdir(".")
			cFileDir.sort()

			print cFileDir
		
			for filesTwo in cFileDir:
				if filesTwo.endswith(outputMatch):
					os.chdir(compDir)
					compF = os.path.realpath(filesTwo)

					print compF

					comp = compF[(compF.rfind('/')+1):]
					comp = comp[:10]

					compD = genfromtxt(compF, delimiter=' ')
					compD = np.delete(compD,0,1)
					compD = np.delete(compD,-1,0)

					resultsM = np.subtract(initialD,compD)
					resultsM = np.absolute(resultsM)
					

					avgVal = LA.norm(np.subtract(initialD,compD), 'fro')
					avgVal = avgVal/2
					avgVal = avgVal/2415
					avgVal = ceil(avgVal * 1000)/1000

					tempRow.append(avgVal)
			print tempRow
			rowwriter.writerow(tempRow)

print "VALIDATION COMPLETE"
