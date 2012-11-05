#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Calculate the estimated maximum average degree as top eigenvalue
# 1 indexed
import os

import scipy.io as sio
import scipy.sparse.linalg.eigen.arpack as arpack
import numpy as np

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time
  
def getMaxAveDegree(G_fn, G = None, lcc_fn = None, roiRootName = None, MADdir = None, eigvDir = None, saveTop = True):
  '''
  Calc the Eigenvalue Max Average Degree of the graph
  Note this is an estimation and is guaranteed to be greater than or equal to the true MAD
  G_fn - filename of the graph .npy
  G - the sparse matrix containing the graph
  lcc_fn - largest connected component of the graph. If none then this is a test case. .npy file
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  toDir - Directory where resulting array is placed
  saveTop - If true save the top 50 eigenvalues
  '''
  print "\nCalcuting maximum average degree..."
  
  if G:
    pass
  
  elif lcc_fn:
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  
  # test case
  else:    
    try:
      G = sio.loadmat(G_fn)['fibergraph']
    except:
      print "file not found %s" % G_fn

  if MADdir:
    eigvl_fn = os.path.join(eigvDir, getBaseName(G_fn) + '_eigvl.npy')
    MAD_fn = os.path.join(MADdir, getBaseName(G_fn) + '_MAD.npy')
    
  else: # test
    eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_eigvl.npy')
    MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_MAD.npy')
      
  numEigs = 100 if (G.shape[0] > 101) else G.shape[0]-2 # Number of eigenvalues to compute
  
  start = time()
  topEigs = (arpack.eigs(G, k = numEigs, which='LR')[0]).real # get eigenvalues, then +ve max REAL part is MAD eigenvalue estimation
  maxAveDeg = np.max(topEigs) 
  print 'Time taken to calc MAD: %f secs' % (time() - start)
  
  print "Saving Top 50 eigenvalues..."
  np.save(MAD_fn ,maxAveDeg)
  
  if (saveTop):
    np.save(eigvl_fn, topEigs)
  
  print "Maxium average degree = ", maxAveDeg
  return maxAveDeg

def main():
    
    parser = argparse.ArgumentParser(description='Calculate Max Avg Degree estimate as max eigenvalue for biggraphs')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    parser.add_argument('MADdir', action='store', help='Full path of directory where you want .npy array resulting file to go')
    parser.add_argument('eigvDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
    
    parser.add_argument('-s', '--saveTop', help='Save the top 50 results to a file' )
    
    result = parser.parse_args()
    if (results.saveTop5):
      getMaxAveDegree(result.G_fn, None, result.lcc_fn, result.roiRootName, result.MADdir, result.eigvDir)
    else:
      getMaxAveDegree(result.G_fn, None, result.lcc_fn, result.roiRootName, result.MADdir, result.eigvDir, False)

if __name__ == '__main__':
  main()
  
