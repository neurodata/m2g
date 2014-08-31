#!/usr/bin/python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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
  @todo: This method
  '''
  print "STUB for SVD check files"

def checkFilesLCC(files = 0):
  '''
  @todo: This method
  '''
  print "STUB for lcc check files"

def main():
  checkFileExtSVD()
  checkFilesLCC()

if __name__ == '__main__':
   main()