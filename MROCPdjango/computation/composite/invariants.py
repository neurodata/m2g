#!/usr/bin/python

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
from scipy.io import loadmat
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils.getBaseName import getBaseName # Duplicates right now
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

def compute(inv_dict):

  if (inv_dict.has_key('G')):
    if inv_dict['G'] is not None:
      pass
  elif (inv_dict['graphsize'] == 'b' or inv_dict['graphsize'] == 'big'):
    G = loadAdjMat(inv_dict['graph_fn'], inv_dict['lcc_fn']) # TODO: test
  # small graphs
  else:
    G = loadmat(inv_dict['graph_fn'])['fibergraph']

  num_nodes = G.shape[0] # number of nodes

  # CC requires deg_fn and tri_fn. Load if available
  if inv_dict['cc']:
    # if either #tri or deg is undefined
    if not inv_dict['tri_fn']:
      inv_dict['tri'] = True
      if not inv_dict['eigvl_fn']:
        inv_dict['eig'] = True
    if not inv_dict['deg_fn']:
      inv_dict['deg'] = True

    cc_array = np.zeros(num_nodes)

  # Only create arrays if the computation will be done
  if inv_dict['tri']:
    if inv_dict['tri_fn']:
      tri_array = np.load(inv_dict['tri_fn']) # load if precomputed
    else:
      tri_array = np.zeros(num_nodes) # local triangle count

  if inv_dict['deg'] or inv_dict['edge']: # edge is global number of edges
    inv_dict['deg'] = True
    if inv_dict['deg_fn']:
      deg_array = np.load(inv_dict['deg_fn'])
    else:
      deg_array = np.zeros(num_nodes) # Vertex degrees of all vertices

  if (inv_dict['ss1']):
    ss1_array = np.zeros(num_nodes) # Induced subgraph edge number i.e scan statistic

  if (not inv_dict['k'] or inv_dict['k'] > 100 or inv_dict['k'] > G.shape[0] - 2):
    k = 100 if G.shape[0]-2 > 101 else G.shape[0] - 2 # Maximum of 100 eigenvalues

  start = time()
  # Calculate Eigenvalues & Eigen vectors
  if (inv_dict['eig'] and not inv_dict['eigvl_fn']):
    l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
    print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)

  # All other invariants
  start = time()
  #### For loop ####
  if (inv_dict['cc'] or inv_dict['ss1'] or (inv_dict['tri'] and not inv_dict['tri_fn'])\
      or (inv_dict['deg'] and not inv_dict['deg_fn'])  ): # one of the others
    for j in range(num_nodes):
      # tri
      if not inv_dict['tri_fn'] and inv_dict['tri']: # if this is still None we need to compute it
        tri_array[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 6.0)) # Divide by six because we count locally

      # ss1 & deg
      if inv_dict['ss1'] or (not inv_dict['deg_fn'] and inv_dict['deg']):
        nbors = G[:,j].nonzero()[0]
        # deg
        if (not inv_dict['deg_fn'] and inv_dict['deg']):
          deg_array[j] = nbors.shape[0]
        # ss1
        if inv_dict['ss1']:
          if (nbors.shape[0] > 0):
            nbors_mat = G[:,nbors][nbors,:]
            ss1_array[j] = nbors.shape[0] + (nbors_mat.nnz/2.0)  # scan stat 1 # Divide by two because of symmetric matrix
          else:
            ss1_array[j] = 0 # zero neighbors hence zero cardinality enduced subgraph

      # cc
      if inv_dict['cc']:
        if (deg_array[j] > 2):
          cc_array[j] = (2.0 * tri_array[j]) / ( deg_array[j] * (deg_array[j] - 1) ) # Jari et al
        else:
          cc_array[j] = 0

    print 'Time taken to compute loop dependent invariants: %f secs\n' % (time() - start)

  ### End For ###
  # global edge
  if inv_dict['edge']:
    edge_count = deg_array.sum()

  # global vertices is num_nodes

  ''' MAD '''
  if (inv_dict['mad']):
    max_ave_deg = np.max(l.real)

  # Computation complete - handle the saving now ...

  ''' Top eigenvalues & eigenvectors '''
  if not inv_dict['eigvl_fn'] and inv_dict['eig'] :
    eigvDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Eigen") #if eigvDir is None else eigvDir

    # Immediately write eigs to file
    inv_dict['eigvl_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
    inv_dict['eigvect_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
    createSave(inv_dict['eigvl_fn'], l.real) # eigenvalues
    createSave(inv_dict['eigvect_fn'], u) # eigenvectors
    print 'Eigenvalues and eigenvectors saved ...'

  ''' Triangle count '''
  if not inv_dict['tri_fn'] and inv_dict['tri']:
    triDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Triangle") #if triDir is None else triDir
    inv_dict['tri_fn'] = os.path.join(triDir, getBaseName(inv_dict['graph_fn']) + '_triangles.npy') # TODO HERE
    createSave(inv_dict['tri_fn'], tri_array)
    print 'Triangle Count saved ...'

  ''' Degree count'''
  if not inv_dict['deg_fn'] and inv_dict['deg']:
    degDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Degree") #if degDir is None else degDir
    inv_dict['deg_fn'] = os.path.join(degDir, getBaseName(inv_dict['graph_fn']) + '_degree.npy')
    createSave(inv_dict['deg_fn'], deg_array)
    print 'Degree saved ...'

  ''' MAD '''
  if inv_dict['mad']:
    MADdir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "MAD") #if MADdir is None else MADdir
    inv_dict['mad_fn'] = os.path.join(MADdir, getBaseName(inv_dict['graph_fn']) + '_mad.npy')
    createSave(inv_dict['mad_fn'], max_ave_deg)
    print 'Maximum Average Degree saved ...'

  ''' Scan Statistic 1'''
  if inv_dict['ss1']:
    ss1Dir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "SS1") #if ss1Dir is None else ss1Dir
    inv_dict['ss1_fn'] = os.path.join(ss1Dir, getBaseName(inv_dict['graph_fn']) + '_scanstat1.npy')
    createSave(inv_dict['ss1_fn'], ss1_array) # save it
    print 'Scan 1 statistic saved ...'

  ''' Clustering coefficient '''
  if inv_dict['cc']:
    ccDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "ClustCoeff") #if ccDir is None else ccDir
    inv_dict['cc_fn'] = os.path.join(ccDir, getBaseName(inv_dict['graph_fn']) + '_clustcoeff.npy')
    createSave(inv_dict['cc_fn'], cc_array) # save it
    print 'Clustering coefficient saved ...'

  ''' Global Vertices '''
  if inv_dict['ver']:
    vertDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Globals") #if vertDir is None else vertDir
    inv_dict['ver_fn'] = os.path.join(vertDir, getBaseName(inv_dict['graph_fn']) + '_numvert.npy')
    createSave(inv_dict['ver_fn'], num_nodes) # save it
    print 'Global vertices number saved ...'

  ''' Global number of edges '''
  if inv_dict['edge']:
    edgeDir = os.path.join(os.path.dirname(inv_dict['graph_fn']), "Globals") #if edgeDir is None else edgeDir
    inv_dict['edge_fn'] = os.path.join(edgeDir, getBaseName(inv_dict['graph_fn']) + '_numedges.npy')
    createSave(inv_dict['edge_fn'], edge_count) # save it
    print 'Global edge number saved ...'

  #if test: # bench test
  #  tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_triangles.npy')
  #  eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
  #  eigvect_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
  #  MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_MAD.npy')

  return inv_dict # TODO: Fix code this breaks. Originally was [tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn]

if __name__ == '__main__':
  print 'This file is not to be called directly. Use helpers'
