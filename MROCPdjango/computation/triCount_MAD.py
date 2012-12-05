#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Estimation of local traingle count & Max avg degree
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

def eignTriLocal_MAD(G_fn, G = None, lcc_fn = None, roiRootName = None, triDir=None, MADdir = None, eigvDir = None, k=None):
  '''
  Local Estimation of Triangle count
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graph
  lcc_fn - largest connected component full filename (.npy)
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXXXX_roi)
  k - Number of eigenvalues to compute. The more the higher accuracy achieved
  triDir - Directory where resulting array is placed
  '''
  print '\nCalculating Eigen triangle count estimation...'

  if (G !=None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']

  n = G.shape[0] # number of nodes
  numTri = np.zeros(n) # local triangle count

  if not (k):
    k =  100 if G.shape[0]-2 > 101 else G.shape[0] - 2

  start = time()
  ''' Calculate Eigenvalues & Eigen vectors'''
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
  print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  start = time()
  ''' Triangle count'''
  for j in range(n):
    numTri[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 6.0)) # Divide by six because we count locally
  print 'Time taken to do triangle calculations: %f secs\n' % (time() - start)


  ''' MAD '''
  maxAveDeg = np.max(l.real)


  ''' Top eigenvalues'''
  # l.real

  #print 'Time taken to calc Num triangles & MAD: %f secs\n' % (time() - start)

  '''write to file '''

  if MADdir:
    eigvl_fn = os.path.join(eigvDir, getBaseName(G_fn) + '_eigvl.npy')
    MAD_fn = os.path.join(MADdir, getBaseName(G_fn) + '_MAD.npy')

  if triDir:
    tri_fn = os.path.join(triDir, getBaseName(G_fn) + '_triangles.npy')

  elif not (MADdir and triDir): # test
    tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_triangles.npy')
    eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_eigvl.npy')
    MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_MAD.npy')

  np.save(MAD_fn ,maxAveDeg)
  np.save(eigvl_fn, l.real)
  np.save(tri_fn, numTri)

  print "MAD, Triangle count & top eigenvalues saved..."

  return tri_fn

def main():
  parser = argparse.ArgumentParser(description='Calculate an estimat of triangle counting on a graph')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
  parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
  parser.add_argument('triDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('MADdir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('eigvDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('k', type = int, action='store', help='The number of Eigenvalues/vectors to compute' )

  result = parser.parse_args()
  eignTriLocal_MAD(result.G_fn, None, result.lcc_fn, result.roiRootName, result.triDir, result.MADdir, result.eigvDir, result.k )

if __name__ == '__main__':
  main()
