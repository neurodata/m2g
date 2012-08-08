'''
@author Disa Mhembere
Module available for download to turn unstructured output of MR one-click pipeline
into a sensible subdir format in accordance with braingraph1's MRN directory
'''
import os
import glob
from shutil import move
import argparse
import string

def convertOneToMany(fromDirName, toDirName):
  '''
  fromDirName - Fully qualified directory holding all fiber, roi, invariants etc.. downloaded from MROC Pipeline
  toDirName - Fully qualified directory where to save the organized data
  '''
  
  fiberPatt = 'fiber.dat'
  roi_rawPatt = 'roi.raw'
  roi_xmlPatt = 'roi.xml'
  smGrPatt = 'fiberSmGr.mat'
  bgGrPatt = 'fiberBgGr.mat'
  lccPatt = 'lcc.npy'
  svdPatt = 'embed.npy'
  
  base = os.path.join(toDirName, 'base')
  
  fiberDir = os.path.join(base, 'fiber')
  roiDir = os.path.join(base, 'roi')
  graphInvDir = os.path.join(base, 'graphInvariants')
  
  graphDir = os.path.join(toDirName, 'graphs')
  smGrDir = os.path.join(graphDir, 'smallgraphs')
  bgGrDir = os.path.join(graphDir, 'biggraphs')
  
  toDirPath = ''
  
  dirs = [fiberDir, roiDir, graphDir, graphInvDir, smGrDir, bgGrDir]
  
  for i in toDirName.split('/')[:-1]:
    toDirPath = i + '/'
  
  ''' Make the dirs that don't alrady exist'''
  for folder in dirs:
    if not os.path.exists(folder):
      os.makedirs(folder) 
    else:
      print folder + ' already exists'
  
  ''' Move files '''
  for theFile in glob.glob(os.path.join(fromDirName,'*')) :
    if theFile[-9:] == fiberPatt:
      if not os.path.exists(os.path.join(fiberDir, theFile.split('/')[-1])): 
        move(theFile,fiberDir)
      else:
        print theFile + ' already exists in ' + fiberDir
    
   # Rois
    elif (theFile[-7:] == roi_rawPatt or theFile[-7:] == roi_xmlPatt):
      if not os.path.exists(os.path.join(roiDir, theFile.split('/')[-1])): 
        move(theFile, roiDir)
      else:
        print theFile + ' already exists in ' + roiDir
    
   # Small graphs
    elif (theFile[-13:] == smGrPatt):
      if not os.path.exists(os.path.join(smGrDir, theFile.split('/')[-1])):
        move(theFile, smGrDir)
      else:
        print theFile + ' already exists in ' + smGrDir
    
    # Big graphs
    elif (theFile[-13:] == bgGrPatt):
      if not os.path.exists(os.path.join(bgGrDir, theFile.split('/')[-1])):
        move(theFile, bgGrDir)
      else:
        print theFile + ' already exists in ' + bgGrDir
        
    # Invariants
    elif (theFile[-7:] == lccPatt or theFile[-9:] == svdPatt):
      if not os.path.exists(os.path.join(graphInvDir, theFile.split('/')[-1])):
        move(theFile, graphInvDir)
      else:
        print theFile + ' already exists in ' + graphInvDir
  
  print 'Done!'
  
def main():
  parser = argparse.ArgumentParser(description='Convert a single dir containing fiber, roi & invariant ')
  parser.add_argument('fromDirName', action='store', help='Directory holding all fiber, roi, invariants etc.. downloaded from MROC Pipeline')
  parser.add_argument('toDirName', action='store', help='Directory where to save the organized data')
  
  result = parser.parse_args()
  convertOneToMany(result.fromDirName, result.toDirName)

if __name__ == '__main__':
  main()
