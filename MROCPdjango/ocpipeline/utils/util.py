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


# util.py
# Created by Disa Mhembere on 2013-02-25.
# Copyright (c) 2013. All rights reserved.
# All heper methods for MROCP views.py

import os
import sys
import zipfile
import tempfile
import re
from random import randint
from django.conf import settings
from django.core.mail import send_mail

def makeDirIfNone(dirPathList):
  '''
  Create a dir specified by dirPathList. Failure usual due to permissions issues.

  @param dirPathList: A 'list' of the full paths of directory(ies) to be created
  '''
  for dirPath in dirPathList:
    try:
      if not (os.path.exists(dirPath)):
        os.makedirs(dirPath)
        print "%s directory made successfully" % dirPath
      else:
        print "%s directory already exists" % dirPath
    except:
      print "[ERROR] while attempting to create %s" % dirPath
      sys.exit(-1)

################################################################################

def getFiberPath(fiberFileName):
  '''
  This returns fiberfn's full path less the 'fiber.dat' portion

  @param fiberFileName - is a tract file name with naming convention '[filename]_fiber.dat'
      where filename may vary but _fiber.dat may not.
  '''
  return fiberFileName.partition('_')[0]

################################################################################

def defDataDirs(projectDir):
  '''
  Define all the paths to the data product directories

  @param projectDir: the fully qualified path of the project directory
  '''
  derivatives = os.path.join(projectDir, 'derivatives')
  #rawdata = os.path.join(projectDir, 'rawdata')
  graphs = os.path.join(projectDir, 'graphs')
  graphInvariants = os.path.join(projectDir, 'graphInvariants')
  #images = os.path.join(projectDir, 'images')

  return [derivatives, graphs, graphInvariants]

################################################################################

def getFiberID(fiberfn):
  '''
  Assumptions about the data made here as far as file naming conventions

  @param fiberfn: the dMRI streamline file in format {filename}_fiber.dat
  '''
  if fiberfn.endswith('/'):
    fiberfn = fiberfn[:-1] # get rid of trailing slash

  if re.match(re.compile(r'.+_fiber$'), os.path.splitext(fiberfn.split('/')[-1])[0]):
    return(os.path.splitext(fiberfn.split('/')[-1])[0]).split('_')[0] + '_'
  else:
    return os.path.splitext(fiberfn.split('/')[-1])[0] + '_'

################################################################################

def writeBodyToDisk(data, saveDir):
  '''
  Write the requests body to disk

  @param data: the data to be written to file
  @param saveDir: the location of where data is to be written

  @return a list with the names of the uplaoded files
  '''
  tmpfile = tempfile.NamedTemporaryFile()
  tmpfile.write ( data )
  tmpfile.flush()
  tmpfile.seek(0)
  rzfile = zipfile.ZipFile ( tmpfile.name, "r" )

  print 'Temporary file created...'

  ''' Extract & save zipped files '''
  uploadFiles = []
  for name in (rzfile.namelist()):
    try:
      outfile = open(os.path.join(saveDir, name.split('/')[-1]), 'wb') # strip name of source folders if in file name
      outfile.write(rzfile.read(name))
      outfile.flush()
      outfile.close()
      uploadFiles.append(os.path.join(saveDir, name.split('/')[-1])) # add to list of files
      print name + " written to disk.."
    except Exception:
      print "\n[WARNING]: Item %s rejected for file download ...\n" % name
  return uploadFiles

################################################################################

def getDirFromFilename(filename):
  '''
  @summary: Get the directort location of a file
  @param filename: the full filename of the file in question
  @return: the directory of the file passed in as a param
  '''
  path = ''
  for part in filename.split('/')[:-1]:
    path += part + '/'
  return path

################################################################################

def adaptProjNameIfReq(projPath):
  '''
  If the directory already exists take a name close to
  the requested one just as file systems do with files
  named the same in a directory

  '''
  if not os.path.exists(projPath):
    return projPath
  else:
    projbase = projPath[:-(len(projPath.split('/')[-1]))]
    scanID = projPath.split('/')[-1]

    while (os.path.exists(projPath)):
      if not (re.match(re.compile('.*_\d+$'), scanID)):
        return  os.path.join(projbase, scanID+'_1')
      else:
        return os.path.join(projbase, addOneToDirNum(scanID))

################################################################################

def addOneToDirNum(dirname):
  '''
  Used for file uploads where file directory match another
  Adds one to the directory number of a directory with
  pattern matching regex = r'.*_\d+$'
  '''
  idx = -1
  char =  dirname[idx]

  while(char != '_'):
    idx -= 1
    char = dirname[idx]

  return dirname[:idx+1] + str(int(dirname[idx + 1:]) + 1)

################################################################################

def saveFileToDisk(fileData, fullFileName):
  '''
  @param f: the file data from a form that is to be saved
  @param fullFileName: the fully qualified file name i.e where it should be stored
    and what it should be named
  '''
  if not os.path.exists(os.path.dirname(fullFileName)):
    os.makedirs(os.path.dirname(fullFileName))
    print "Making directory: %s ..." % os.path.dirname(fullFileName)

  destination = open(fullFileName, 'wb+') # Consider try: except for this
  for chunk in fileData.chunks():
      destination.write(chunk)
  destination.close()

  print "Saving file: %s " % fullFileName

################################################################################

def sendJobBeginEmail(email_addr, invariants, genGraph=True):

  msg = "Hello,\n\nThe following actions were requested using %s:\n" % email_addr

  if genGraph:
    msg += "- Generate graph\n"+" "*randint(0,10)

  for inv in invariants:
    msg += "- Compute " + settings.VALID_FILE_TYPES[inv] + "\n"

  msg +=  "\nFeel free to close your browser window or start a new job. Your current job will not be affected. You will receive another email when your job completes."
  msg += " "*randint(0,10)
  msg += "\n\nThanks for using MROCP,\nThe MROCP team"
  msg += " "*randint(0,10)

  send_mail("MROCP: Graph job request",
            msg, settings.SERVER_EMAIL, [email_addr], fail_silently=False)

def sendJobFailureEmail(email_addr, msg):
  msg += "Thanks for using MROCP,\nThe MROCP team"

  send_mail("MROCP: Graph job FAILURE!",
            msg, settings.SERVER_EMAIL, [email_addr], fail_silently=False)

def sendJobCompleteEmail(email_addr, dataLoc):
  msg = "Congratulations,\n\nThe MROCP job you requested is complete and available for download at %s" % dataLoc
  msg += " "*randint(0,10)
  msg += "\n\nThanks for using MROCP,\nThe MROCP team"

  send_mail("MROCP: Graph job COMPLETE!",
            msg, settings.SERVER_EMAIL, [email_addr], fail_silently=False)

#####################################################################################

def get_genus(fn):
  """
  Get the genus given a file path

  @param fn: the genus directory name
  """

  sep = "/"
  genera = os.listdir(settings.GRAPH_DIR)
  for idx, name in enumerate(fn.split(sep)):
    if name in genera: 
      return name

  print "No genus found!"
  return "" # Unknown