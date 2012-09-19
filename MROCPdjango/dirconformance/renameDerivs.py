'''
@author Disa Mhembere
Module available for download at [1]: https://github.com/openconnectome/MR-connectome/tree/master/MROCPdjangoForm/dirconformanceto
turn a dir with filenames in any dir in accordance with braingraph1's MRN directory

Takes into account files with correct naming convention already. Only affects a single dataset.
** USE Caution when using

Dependencies - python 2.7 or later, convertToReqd.py from source[1]
usage: from terminal/command line. For help, 'cd' into containing directory & type:
 python renameDerivs.py -h
'''

import os
import re
import sys
import argparse
import shutil
from glob import glob

from convertToReqd import makeBrandNewDir

def renameFiles(projDir, duplicateDir = None):
  
  ''' Make duplicateDir if we are duplicating data '''
  if (duplicateDir):
    makeBrandNewDir(duplicateDir)
  
  ''' get folder names within the project directory '''
  derivDirs = os.listdir(projDir)
  
  ''' Used in regex matching'''
  fiberPatt = 'fiber'
  
  roiPatt = 'roi'
  faPatt = 'fa'
  connMtxPatt = 'connMtx'
  maskPatt = 'mask'
  sstripPatt = 'sstrip'
  tensor = 'tensor'
  
  mapping = {roiPatt:['_roi.raw','_roi.xml'],faPatt:['_fa.raw', '_fa.xml'] \
    , maskPatt:['_mask.raw', '_mask.xml'], fiberPatt:['_fiber.dat'], \
    sstripPatt:['_sstrip.raw','_sstrip.xml'], tensor:['_tensor.raw','_tensor.xml']}
  
  CmtxMap = { connMtxPatt:'connMtx.csv'}
  
  for folder in derivDirs:
    if not folder.startswith('.'):
      ''' dMRI streamlines & connMtx'''
      for patt in CmtxMap:
        if (re.match(re.compile(patt, re.IGNORECASE),folder)): # regex match of deriv dir name - case insensitive
          for theFile in os.listdir((os.path.join(projDir,folder))):
            ext = os.path.splitext(theFile)[1] # file extension
            if not duplicateDir:
              if not (theFile[-(len(patt)+len(ext)):] == CmtxMap[patt]):
                os.rename(os.path.join(projDir,folder,theFile), os.path.join(projDir,folder, theFile[:-len(ext)] + CmtxMap[patt]))
              else:
                print 'Already named correctly: ' + theFile
            else: 
              if not (os.path.exists(os.path.join(duplicateDir, folder))):
                os.makedirs(os.path.join(duplicateDir, folder)) # Make reqd dir if non-existent
              if not (theFile[-(len(patt)+len(ext)):] == CmtxMap[patt]):
                shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir, folder , theFile[:-len(ext)] + CmtxMap[patt]))
              else:
                print 'Already named correctly' + theFile
                shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir, folder , theFile))
      
      ''' All other files which mainly have 2 parts i.e .xml & .raw parts ''' 
      for patt in mapping:
        if ( re.match(re.compile(patt,re.IGNORECASE),folder)):
          for theFile in os.listdir((os.path.join(projDir,folder))):
            ext = os.path.splitext(theFile)[1] # file extension
            if not duplicateDir:
              if os.path.splitext(theFile)[1] == '.raw':
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][0]):
                  os.rename(os.path.join(projDir,folder,theFile),os.path.join(projDir,folder, theFile[:-len(ext)] + mapping[patt][0]))
                else:
                  print 'CORRECT Name: ' + theFile
              elif os.path.splitext(theFile)[1] == '.xml':
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][1]):
                  os.rename(os.path.join(projDir,folder,theFile), os.path.join(projDir, folder, theFile[:-len(ext)] + mapping[patt][1]))
                else:
                  print 'CORRECT Name: ' + theFile
              
              elif os.path.splitext(theFile)[1] == '.dat':
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][0]):
                  os.rename(os.path.join(projDir,folder,theFile), os.path.join(projDir, folder, theFile[:-len(ext)] + mapping[patt][0]))
                else:
                  print 'CORRECT Name: ' + theFile
            
            # Option to duplicate data is chosen      
            elif duplicateDir:
              if os.path.splitext(theFile)[1] == '.raw':
                if not (os.path.exists(os.path.join(duplicateDir, folder))):
                  os.makedirs(os.path.join(duplicateDir, folder))
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][0]):
                  shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir,folder, theFile[:-len(ext)] + mapping[patt][0]))
                else:
                  print 'CORRECT Name: ' + theFile
                  shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir,folder, theFile))
                  
              elif os.path.splitext(theFile)[1] == '.xml':
                if not (os.path.exists(os.path.join(duplicateDir, folder))):
                  os.makedirs(os.path.join(duplicateDir, folder))
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][1]):
                  shutil.copy2(os.path.join(projDir,folder,theFile),os.path.join(duplicateDir,folder, theFile[:-len(ext)] + mapping[patt][1]))
                else:
                  print 'CORRECT Name: ' + theFile
                  shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir,folder, theFile))
                  
              elif os.path.splitext(theFile)[1] == '.dat':
                if not (os.path.exists(os.path.join(duplicateDir, folder))):
                  os.makedirs(os.path.join(duplicateDir, folder))
                if not (theFile[-(len(patt)+len(ext)+1):] == mapping[patt][0]):
                  shutil.copy2(os.path.join(projDir,folder,theFile),os.path.join(duplicateDir,folder, theFile[:-len(ext)] + mapping[patt][0]))
                else:
                  print 'CORRECT Name: ' + theFile
                  shutil.copy2(os.path.join(projDir,folder,theFile), os.path.join(duplicateDir,folder, theFile))
                  
  print "\nCompleted successfully!"
def main():
  parser = argparse.ArgumentParser(description='Convert a dir with any filename convention to match reqd for MROCP.\
                                   The projDir must have at least fiber & roi subdirectory')
  parser.add_argument('projDir', action='store', nargs = '+' ,help='Directory holding all fiber, roi, invariants etc.. downloaded from MROC Pipeline')
  
  result = parser.parse_args()
  
  if len(result.projDir) > 1:
    renameFiles(result.projDir[0], result.projDir[1])
  else:
    renameFiles(result.projDir[0])
  
if __name__ == '__main__':
  main()
  
