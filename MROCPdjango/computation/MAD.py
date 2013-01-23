#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Max average degree of a sparse graph

import os
import scipy.io as sio
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time

def calcMAD(G_fn, G = None, lcc_fn = None, roiRootName = None,  MADdir = None, eigvDir = None, k=None):
  '''
  Estimation of the maximum average degree
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graph
  lcc_fn - largest connected component full filename (.npy)
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXXXX_roi)
  MADdir - the directory where the file holding the MADdir should go
  k - Number of eigenvalues to compute. The more the higher accuracy achieved
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
    k =  100 if G.shape[0]-2 > 101 else G.shape[0]

  start = time()
  ''' Calculate Eigenvalues & Eigen vectors'''
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
  print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  eigvalDir = os.path.join(eigvDir,"values")
  eigvectDir = os.path.join(eigvDir,"vectors")

  if not os.path.exists(eigvalDir):
    os.makedirs(eigvalDir)
  if not os.path.exists(eigvectDir):
    os.makedirs(eigvectDir)


  ''' MAD '''
  maxAveDeg = np.max(l.real)

  '''write to file '''

  if MADdir:
    eigvl_fn = os.path.join(eigvalDir, getBaseName(G_fn) + '_eigvl.npy')
    eigvect_fn = os.path.join(eigvectDir, getBaseName(G_fn) + '_eigvect.npy')
    MAD_fn = os.path.join(MADdir, getBaseName(G_fn) + '_MAD.npy')

  elif not (MADdir and triDir): # test
    eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_eigvl.npy')
    MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_MAD.npy')

  np.save(MAD_fn ,maxAveDeg)
  np.save(eigvl_fn, l.real)
  np.save(eigvect_fn, u) # save eigenvectors

  print "MAD & top eigenvalues saved..."
  return [MAD_fn, eigvl_fn, eigvect_fn] # Change here may break other code

def main():
  parser = argparse.ArgumentParser(description='Calculate an estimat of triangle counting on a graph')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
  parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
  parser.add_argument('MADdir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('eigvDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('k', type = int, action='store', help='The number of Eigenvalues/vectors to compute' )

  result = parser.parse_args()
  calcMAD(result.G_fn, None, result.lcc_fn, result.roiRootName, result.MADdir, result.eigvDir, result.k )

if __name__ == '__main__':
  main()
