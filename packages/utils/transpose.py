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

a=open(params[2],'w')

with open(params[1]) as f:
	lis=[x.split(' ') for x in f]

print zip(*lis)

for x in zip(*lis):
  	for y in x:
    		a.write(y+' ')
  	a.write('\n')

f.close()
a.close()

os.remove(params[1])
