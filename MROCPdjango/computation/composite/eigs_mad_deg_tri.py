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
'''
def eigs_mad_deg_tri(inv_dict['graph_fn'], G=None, lcc_fn=None, triDir=None, MADdir = None,\
                         eigvDir=None, degDir=None, k=None, eig=False, tri=False, mad=False, deg=False, test=False):

  All invariants that require the top k eigenvalues computed can be computed here.
  Only exception is degree which is here because clustering coefficient requires
  triangle number + degree. Best to compute both here if reqd.

  Which ones you want computed is a choice based on params

  @param inv_dict['graph_fn']: fibergraph full filename (.mat)
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

def eigs_mad_deg_tri(inv_dict):
  returnDict = dict()

  if (inv_dict.has_key('G')):
    if inv_dict['G'] is not None:
      pass
  elif (inv_dict['graphsize'] == 'b' or inv_dict['graphsize'] == 'big'):
    G = loadAdjMat(inv_dict['graph_fn'], inv_dict['lcc_fn']) # TODO: test
  # small graphs
  else:
    G = loadmat(inv_dict['graph_fn'])['fibergraph']

  numNodes = G.shape[0] # number of nodes

  # Only create arrays if the computation will be done
  if (inv_dict['tri']):
    numTri = np.zeros(numNodes) # local triangle count
  if (inv_dict['deg']):
    vertxDeg = np.zeros(numNodes) # Vertex degrees of all vertices
  if not (k):
    k = 100 if G.shape[0]-2 > 101 else G.shape[0] - 2 # Maximum of 100 eigenvalues

  start = time()
  ''' Calculate Eigenvalues & Eigen vectors'''
  l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
  print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  start = time()

  ''' Compute invariants dependent on eigs '''
  if (inv_dict['tri'] or inv_dict['deg']): # one of the others
    for j in range(numNodes):
      if not inv_dict['tri_fn'] and inv_dict['tri']: # if this is still None we need to compute it
        numTri[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 6.0)) # Divide by six because we count locally

      if not inv_dict['deg_fn'] and inv_dict['deg']:
        vertxDeg[j] = G[j,:].nonzero()[1].shape[0]
    print 'Time taken to compute eig dependent invariants: %f secs\n' % (time() - start)

  ''' MAD '''
  if (inv_dict['mad']):
    maxAveDeg = np.max(l.real)

  # Computation complete - handle the saving now ...

  ''' Triangle count '''
  if not inv_dict['tri_fn'] and inv_dict['tri']:
    triDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Triangle") #if triDir is None else triDir
    inv_dict['tri_fn'] = os.path.join(triDir, getBaseName(inv_dict['graph_fn']) + '_triangles.npy') # TODO HERE
    createSave(inv_dict['tri_fn'], numTri)
    print 'Triangle Count saved ...'

  ''' Degree count'''
  if not inv_dict['deg_fn'] and inv_dict['deg']:
    degDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Degree") #if degDir is None else degDir
    inv_dict['deg_fn'] = os.path.join(degDir, getBaseName(inv_dict['graph_fn']) + '_degree.npy')
    createSave(inv_dict['deg_fn'], vertxDeg)
    print 'Degree saved ...'

  ''' MAD '''
  if not inv_dict['mad_fn'] and inv_dict['mad']:
    MADdir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "MAD") #if MADdir is None else MADdir
    inv_dict['mad_fn'] = os.path.join(MADdir, getBaseName(inv_dict['graph_fn']) + '_mad.npy')
    createSave(inv_dict['mad_fn'], maxAveDeg)
    print 'Maximum Average Degree saved ...'

  ''' Top eigenvalues & eigenvectors '''
  if not inv_dict['eigvl_fn'] and inv_dict['eig'] : # If there is no eigvl_fn there is no eigvect_fn
    eigvDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Eigen") if eigvDir is None else eigvDir
    eigvalDir = os.path.join(eigvDir,"values")
    eigvectDir = os.path.join(eigvDir,"vectors")

    # Immediately write eigs to file
    inv_dict['eigvl_fn'] = os.path.join(eigvalDir, getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
    inv_dict['eigvect_fn'] = os.path.join(eigvectDir, getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
    createSave(inv_dict['eigvl_fn'], l.real) # eigenvalues
    createSave(inv_dict['eigvect_fn'], u) # eigenvectors
    print 'Eigenvalues and eigenvectors saved ...'

  #if test: # bench test
  #  tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_triangles.npy')
  #  eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
  #  eigvect_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
  #  MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_MAD.npy')

  return inv_dict # TODO: Fix code this breaks. Originally was [tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn]

if __name__ == '__main__':
  print 'This file is not to be called directly. Use helpers'
