#!/usr/bin/python

"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: Insert the correct files into the processing tools
This script checks file extensions through regular expression
It assumes no more than 1 file type per upload
"""

import re

def checkFileExtGengraph(files):
  '''
  Check the file extensions of a set of files used in MROCP

  @param files: the files to check
  @type files: string
  '''
  for fileName in files:

    if re.match(re.compile( r'.+\.xml'), fileName) != None:
      xmlFileName = fileName

    if re.match(re.compile( r'.+\.dat'), fileName) != None:
      datFileName = fileName

    if re.match( re.compile( r'.+\.raw'), fileName) != None:
      rawFileName = fileName

  return [xmlFileName, datFileName, rawFileName]

def checkFileExtSVD(files = 0):
  '''
  @todo
  '''
  print "STUB for SVD check files"

def checkFilesLCC(files = 0):
  '''
  @todo
  '''
  print "STUB for lcc check files"

def main():
  checkFileExtSVD()
  checkFilesLCC()

if __name__ == '__main__':
   main()
