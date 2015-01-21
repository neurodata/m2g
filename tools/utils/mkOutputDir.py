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


# read in command line args
params = list(argv)

# Create dir name
resultsD="results" + datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
directory = os.path.join(params[1],resultsD)

# Create directory
os.makedirs(directory)
print "#@@# " + directory + " #@@#"
