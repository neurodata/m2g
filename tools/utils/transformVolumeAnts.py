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
import string
from sys import exit
import sys
import re
import os
import scipy.io
from subprocess import Popen,PIPE

os.environ['DISPLAY'] = 'localhost:99.0'

# read in command line args
params = list(argv)

classpath = params[1]
volume = params[3]
volumes = params[4]
xDir = params[5]
xFile = params[6]

# Read File
inFile = open(params[2])
buffer = []
keepCurrentSet = True
pointer = 0
matrix = "\""
for line in inFile:
	if pointer > 1:
		if pointer < 6:		
			matrix += line
			matrix += ";"
	pointer += 1
matrix = matrix[:-2]
matrix += "\""
inFile.close()

#args = ["/mnt/pipelineShare/tools/mrcap/mipav/jre/bin/java"] + ["-classpath"] + [classpath] + ["edu.jhu.ece.iacl.jist.cli.run"] + ["edu.jhu.ece.iacl.plugins.registration.MedicAlgorithmTransformVolume"] + ["-inVolumes"] + [volumes] + ["-inVolume"] + [volume] + ["-inTransformation"] + [matrix] + ["-xDir"] + [xDir] + ["-xFile"] + [xFile]
#print args

# Call MedicAlgorithmTransformVolume.java
#process = Popen(args, stdout=PIPE, stderr=PIPE)
#output = process.communicate()
#proc_error = output[1]
#proc_output = output[0]
#exit_code = process.wait()
	

# Print Matrix
#print "#@@# " + matrix + " #@@#"
#print proc_error
#print proc_output



