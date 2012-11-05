#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Estimation of local traingle count
# Based on work by: Charalampos E. Tsourakakis
# Published as: Counting Triangles in Real-World Networks using Projections

import os
import scipy.io as sio
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time

def eignTriangleLocal(G_fn, G = None, lcc_fn = None, roiRootName = None, triDir=None, k=None):
  '''
  Local Estimation of Triangle count
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graph
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXXXX_roi)
  k - Number of eigenvalues to compute. The more the higher accuracy achieved
  triDir - Directory where resulting array is placed
  '''
  print '\nCalculating Eigen triangle count estimation...'
  
  if G:
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
  
  n = G.shape[0] # number of nodes
  numTri = np.zeros(n) # local triangle count
  
  if not (k):
    k =  100 if G.shape[0]-2 > 101 else G.shape[0]
  
  start = time()
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0) 
  
  for j in range(n):
    numTri[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 6.0)) # Divide by six because we count locally
  
  print 'Time taken to calc Num triangles: %f secs\n' % (time() - start)
  
  '''write to file '''
  
  if triDir:
    tri_fn = os.path.join(triDir, getBaseName(G_fn) + '_triangles.npy')
      
  else: # test
    tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_triangles.npy')

  np.save(tri_fn, numTri)
  return tri_fn

def main():
  parser = argparse.ArgumentParser(description='Calculate an estimat of triangle counting on a graph')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
  parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
  parser.add_argument('triDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('k', type = int, action='store', help='The number of Eigenvalues/vectors to compute' )
  
  result = parser.parse_args()
  eignTriangleLocal(result.G_fn, None, result.lcc_fn, result.roiRootName,result.triDir, result.k )

if __name__ == '__main__':
  main()