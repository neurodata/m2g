#!/usr/bin/python

## Make a directory based on input parent directory and desired directory name ##
## mkDir(parentDir, dirName)

############################################################################################
## (c) 2012 The Johns Hopkins University / Applied Physics Laboratory.  All Rights Reserved.
## Proprietary Until Publicly Released
############################################################################################

from sys import argv
import string
import random
import os


# read in command line args
params = list(argv)

# Read File
fyle = open(params[1])
print "opened file"

# Loop to find value
lines = fyle.readlines()
print "read lines"
for line in lines:
	print params[2]
	print line.startswith(params[2])
	if line.startswith(params[2]):
		param, value = line.split("=",1)
		value = value[:-1]
		print "#@@# " + value + " #@@#"
