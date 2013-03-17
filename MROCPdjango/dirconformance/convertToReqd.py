'''
@author : Disa Mhembere
Module available for upload to convert from a dir struct like braingraph1's MRN to
 a single dir with no structure

dependencies - python 2.7 or later
usage: from terminal/command line. For help, 'cd' into containing directory & type:
 python convertToReqd.py -h
'''
import os, sys, shutil
from glob import glob
import argparse

def convertManyToSingle(fromDirName, toDirName):
  '''
  fromDirName - full name of the dir where data is located initially
  toDirName - full name of the dir to be created where data should go. Cannot be already created
  '''
  
  ''' Get fiber & roi directory names'''
  fiberDir = os.path.join(fromDirName,'fiber')
  roiDir = os.path.join(fromDirName,'roi')
  
  ''' Make new single dir if it doesn't exist''' 
  toDirName = makeBrandNewDir(toDirName)
  
  ''' Move files from fiber & roi dirs '''  
  for folder in [fiberDir, roiDir]:
    for theFile in glob(os.path.join(folder,'*')):
      shutil.copy(theFile, toDirName)
 
def makeBrandNewDir(newDir):
  '''
  newDir - The name of the new directory you want to create
  '''
  orignNewDir = newDir
  namingCount = 1
  
  if not (os.path.exists(newDir)):
    try:
      os.makedirs(newDir)
      print 'New dir made: ' + newDir
      return newDir
    except:
      print 'Permissions problem, try to save in another location'
      
  else:
    while (os.path.exists(newDir)):
      print newDir + ' is already in use. Rename underway..'
      namingCount += 1
      newDir = orignNewDir + '(' + str(namingCount) + ')'
      
  try:
    os.makedirs(newDir)
    print 'New dir made: ' + newDir
    return newDir
  except:
    print 'Permissions problem, try to save in another location'
  
def main():
  parser = argparse.ArgumentParser(description='Convert a dir struct containing fiber, roi sub-dirs to a single holding only fiber & roi files')
  parser.add_argument('fromDirName', action='store', help='full name of the dir where data is located initially')
  parser.add_argument('toDirName', action='store', help='full name of the dir to be created where data should go. Cannot be already created')
  
  result = parser.parse_args()
  convertManyToSingle(result.fromDirName, result.toDirName)
  
if __name__ == '__main__':
  main()
  
