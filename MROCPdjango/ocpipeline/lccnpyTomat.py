#!/usr/bin/python
"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: Module to convert files from 1 format to the next
"""

import scipy.io as sio
import numpy as np
import os
import argparse

def convertLCCtoMat(lcc_fn, toDir):
  '''
  Convert a npy largest connected components file to an equivalent .mat file

  @param lcc_fn: largest connected components full file name which should be a .npy
  @type lcc_fn: string

  @param toDir: where to save the result
  @type toDir: string
  '''
  lcc = np.load(lcc_fn).item().toarray()
  mat_fn = os.path.join(toDir, os.path.splitext(lcc_fn.split('/')[-1])[0])
  sio.savemat(os.path.splitext(mat_fn)[0],{'lcc': lcc}, appendmat = True)
  print ('%s sucessfully saved as mat') % os.path.splitext(lcc_fn.split('/')[-1])[0]

def main():

    parser = argparse.ArgumentParser(description='Convert directory of derivatives to .mat format')
    parser.add_argument('fromDir', action='store',help='Full path of directory containing .npy files to be converted')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .mat file to go')

    result = parser.parse_args()

    if not os.path.exists(result.toDir):
      os.makedirs(result.toDir)

    for theFile in os.listdir(result.fromDir):
      if not (result.fromDir.startswith('.')):
        convertLCCtoMat(os.path.join(result.fromDir, theFile), result.toDir)

if __name__ == '__main__':
  main()
