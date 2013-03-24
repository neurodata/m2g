#!/usr/bin/python

# eigs_mad_deg_tri.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
from scipy.io import loadmat
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils import getBaseName # Duplicates right now
from computation.utils import loadAdjMatrix # Duplicates right now

import argparse
from time import time

from computation.utils.file_util import createSave

# function originally called eignTriLocal_deg_MAD
def eigs_mad_deg_tri(G_fn, G=None, lcc_fn=None, triDir=None, MADdir = None,\
                         eigvDir=None, degDir=None, k=None, eig=False, tri=False, mad=False, deg=False, test=False):
  '''
  All invariants that require the top k eigenvalues computed can be computed here.
  Only exception is degree which is here because clustering coefficient requires
  triangle number + degree. Best to compute both here if reqd.

  Which ones you want computed is a choice based on params

  @param G_fn: fibergraph full filename (.mat)
  @param G: the sparse matrix containing the graph
  @param lcc_fn: largest connected component full filename (.npy)
  @param k: Number of eigenvalues to compute. The more the higher accuracy achieved
  @param triDir: Directory where resulting array is placed
  @param degDir: Directory where to place local degree result

  # Invariant options

  @param eig: Compute eigs? True for yes else no. If eigvDir is given assumed to be True
  @param tri: Count triangles? True for yes else no. If triDir is given assumed to be True
  @param deg: Compute local degree? True for yes else False. If degDir assumed to be True
  @param mad: Compute max ave degree? True for yes else no. If MADdir is given assumed to be True

  @return returnDict: a dict with the attribute & its filename # TODO: May change
  '''

  returnDict = dict()

  #print '\nCalculating Eigen triangle count estimation...'
  if (G is not None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn)
  # test case
  else:
    G = loadmat(G_fn)['fibergraph']

  numNodes = G.shape[0] # number of nodes

  # Only create arrays if the computation will be done
  if (triDir or tri):
    numTri = np.zeros(numNodes) # local triangle count
  if (degDir or deg):
    vertxDeg = np.zeros(numNodes) # Vertex degrees of all vertices
  if not (k):
    k = 100 if G.shape[0]-2 > 101 else G.shape[0] - 2 # Maximum of 100 eigenvalues

  start = time()
  ''' Calculate Eigenvalues & Eigen vectors'''
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
  print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  start = time()

  ''' Computer invariants dependent on eigs '''
  if (triDir or tri or degDir or deg): # one of the others
    for j in range(numNodes):
      if (locals().has_key('numTri')): # If this is created we must want to compute this
        numTri[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 6.0)) # Divide by six because we count locally

      if (locals().has_key('vertxDeg')):
        vertxDeg[j] = G[j,:].nonzero()[1].shape[0]
    print 'Time taken to compute eig dependent invariants: %f secs\n' % (time() - start)

  ''' MAD '''
  if (mad or MADdir):
    maxAveDeg = np.max(l.real)

  # Computation complete - handle the saving now ...

  ''' Triangle count '''
  if locals().has_key('numTri'):
    triDir = os.path.join(os.path.dirname(G_fn), "Triangle") if triDir is None else triDir
    tri_fn = os.path.join(triDir, getBaseName(G_fn) + '_triangles.npy')
    createSave(tri_fn, numTri)

    returnDict['tri_fn'] = tri_fn
    print 'Triangle Count saved ...'

  ''' Degree count'''
  if locals().has_key('vertxDeg'):
    degDir = os.path.join(os.path.dirname(G_fn), "Degree") if degDir is None else degDir
    deg_fn = os.path.join(degDir, getBaseName(G_fn) + '_degree.npy')
    createSave(deg_fn, vertxDeg)

    returnDict['deg_fn'] = deg_fn
    print 'Degree saved ...'

  ''' MAD '''
  if locals().has_key('maxAveDeg'):
    MADdir = os.path.join(os.path.dirname(G_fn), "MAD") if MADdir is None else MADdir
    MAD_fn = os.path.join(MADdir, getBaseName(G_fn) + '_MAD.npy')
    createSave(MAD_fn, maxAveDeg)

    returnDict['MAD_fn'] = MAD_fn
    print 'Maximum Average Degree saved ...'

  ''' Top eigenvalues & eigenvectors '''
  if (eig or eigvDir):
    eigvDir = os.path.join(os.path.dirname(G_fn), "Eigen") if eigvDir is None else eigvDir
    eigvalDir = os.path.join(eigvDir,"values")
    eigvectDir = os.path.join(eigvDir,"vectors")

    # Immediately write eigs to file
    eigvl_fn = os.path.join(eigvalDir, getBaseName(G_fn) + '_eigvl.npy')
    eigvect_fn = os.path.join(eigvectDir, getBaseName(G_fn) + '_eigvect.npy')
    createSave(eigvl_fn, l.real) # eigenvalues
    createSave(eigvect_fn, u)# eigenvectors

    returnDict['eigvl_fn'] = eigvl_fn
    returnDict['eigvect_fn'] = eigvect_fn
    print 'Eigenvalues and eigenvectors saved ...'

  if test: # bench test
    tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_triangles.npy')
    eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_eigvl.npy')
    eigvect_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_eigvect.npy')
    MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_MAD.npy')

  return returnDict # TODO: Fix code this breaks. Originally was [tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn]

#def main():
#  parser = argparse.ArgumentParser(description='Calculate an estimat of triangle counting on a graph')
#  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
#  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
#  parser.add_argument('triDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
#  parser.add_argument('MADdir', action='store', help='Full path of directory where you want .npy array resulting file to go')
#  parser.add_argument('eigvDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
#  parser.add_argument('degDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
#  parser.add_argument('k', type = int, action='store', help='The number of Eigenvalues/vectors to compute' )
#
#  result = parser.parse_args()
#  eigs_mad_deg_tri(result.G_fn, None, result.lcc_fn, result.triDir, result.MADdir, result.eigvDir, result.degDir, result.k )

if __name__ == '__main__':
  print 'This file is not to be called directly. Use helpers'
