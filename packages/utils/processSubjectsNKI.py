#!/usr/bin/python

## Wrapper For transverse synapse detector workflow##

## This wrapper exists to facilitate workflow level parallelization inside the LONI pipeline until
## it is properly added to the tool.  It is important for this step to do workflow level parallelization
## because of the order of processing.
##
## Make sure that you specify the environment variable MATLAB_EXE_LOCATION inside the LONI module.  This can be
## set under advanced options on the 'Execution' tab in the module set up.
############################################################################################
## (c) 2012 The Johns Hopkins University / Applied Physics Laboratory.  All Rights Reserved.
## Proprietary Until Publicly Released
############################################################################################

from sys import argv
import datetime
import string
import os


# read in command line args
params = list(argv)

subjDirectory = params[1]
outputDirectory = params[2]

# Find File Names
os.chdir(subjDirectory)
for files in os.listdir("."):
	if files.endswith(".b"):
		print "#B# " + os.path.abspath(files) + " #B#"
	elif files.endswith(".grad"):
		print "#GRAD# " + os.path.abspath(files) + " #GRAD#"
	elif files.endswith("dti.nii.gz"):
		print "#DTI# " + os.path.abspath(files) + " #DTI#"
	elif files.endswith("mprage.nii.gz"):
		print "#MPRAGE# " + os.path.abspath(files) + " #MPRAGE#"
	

# Make Output Directory
basename=os.path.basename
subDir=os.path.join(outputDirectory,basename(subjDirectory))
print "#@@@# " + subDir + " #@@@#"
#os.makedirs(subDir)



