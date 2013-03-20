#!/usr/bin/python

# util.py
# Created by Disa Mhembere on 2013-02-25.
# Copyright (c) 2013. All rights reserved.
# All heper methods for MROCP views.py

import os
import sys
import zipfile
import tempfile
import re


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
  rawdata = os.path.join(projectDir, 'rawdata')
  graphs = os.path.join(projectDir, 'graphs')
  graphInvariants = os.path.join(projectDir, 'graphInvariants')
  images = os.path.join(projectDir, 'images')

  return [derivatives, rawdata, graphs, graphInvariants, images]

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
    outfile = open(os.path.join(saveDir, name.split('/')[-1]), 'wb') # strip name of source folders if in file name
    outfile.write(rzfile.read(name))
    outfile.flush()
    outfile.close()
    uploadFiles.append(os.path.join(saveDir, name.split('/')[-1])) # add to list of files
    print name + " written to disk.."
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

def convertFiles(uploadedFiles, fileType , toFormat, convertFileSaveLoc):
  '''
  Helper method to call convertTo module for invariant and graph format conversion

  @param uploadedFiles: array with all file names of uploaded files
  @param fileType
  @param toFormat -
  @param convertFileSaveLoc -
  @return correctFileFormat - check if at least one file has the correct format
  @return correctFileType - check if file type is legal
  '''
  for file_fn in uploadedFiles:
    # determine type of the file
    if (os.path.splitext(file_fn)[1] in ['.mat','.csv','.npy']):
      correctFileFormat = True
      if (fileType == 'fg' or fileType == 'fibergraph'):
        correctFileType = True
        pass # TODO : DM
      elif( fileType == 'lcc' or fileType == 'lrgstConnComp'):
        correctFileType = True
        pass # TODO : DM
      elif (fileType in settings.VALID_FILE_TYPES.keys() or fileType in settings.VALID_FILE_TYPES.values()):
        # Check if file format is the same as the toFormat
        if (os.path.splitext(file_fn)[1] in toFormat):
          toFormat.remove(os.path.splitext(file_fn)[1])
        if (len(toFormat) == 0):
          pass # No work to be done here
        else:
          correctFileType = True
          convertTo.convertAndSave(file_fn, toFormat, convertFileSaveLoc, fileType) # toFormat is a list
  return correctFileFormat, correctFileType

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