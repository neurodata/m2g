#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Eigenvalues of a sparse graph

import os
import scipy.io as sio
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time

def calcEigs(G_fn, G = None, lcc_fn = None, roiRootName = None,  eigvDir = None, k=None):
  '''
  Calculate the top k eigenvalues
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graph
  lcc_fn - largest connected component full filename (.npy)
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXXXX_roi)
  eigvDir - full directory path of where eigenvalues array should be saved
  k - Number of eigenvalues to compute. The more the higher accuracy achieved
  '''
  print '\nCalculating Eigenvalues...'

  if (G !=None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']

  n = G.shape[0] # number of nodes

  if not (k):
    k =  100 if G.shape[0]-2 > 101 else G.shape[0]

  start = time()
  ''' Calculate Eigenvalues & Eigen vectors'''
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
  print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  eigvl_fn = os.path.join(eigvDir, getBaseName(G_fn) + '_eigvl.npy')
  np.save(eigvl_fn, l.real)

  print "Top eigenvalues saved..."

def main():
  parser = argparse.ArgumentParser(description='Calculate an estimat of triangle counting on a graph')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
  parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
  parser.add_argument('eigvDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
  parser.add_argument('k', type = int, action='store', help='The number of Eigenvalues/vectors to compute' )

  result = parser.parse_args()
  calcEigs(result.G_fn, None, result.lcc_fn, result.roiRootName, result.eigvDir, result.k )

if __name__ == '__main__':
  main()
