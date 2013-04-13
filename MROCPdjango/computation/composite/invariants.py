#!/usr/bin/python

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils.getBaseName import getBaseName # Duplicates right now
from computation.utils import loadAdjMatrix # Duplicates right now
from computation.utils.file_util import loadAnyMat
from computation.utils.loadAdjMatrix import loadAdjMat

import argparse
from time import time
from computation.utils.file_util import createSave

def compute(inv_dict, save=True):
  '''
  @param inv_dict: is a dict optinally containing any of these:
    - inv_dict['edge']: boolean for global edge count
    - inv_dict['ver']: boolean for global vertex number
    - inv_dict['tri']: boolean for local triangle count
    - inv_dict['tri_fn']: the path of a precomputed triangle count (.npy)
    - inv_dict['eig']: boolean for eigenvalues and eigenvectors
    - inv_dict['eigvl_fn']: the path of a precomputed eigenvalues (.npy)
    - inv_dict['eigvect_fn']: the path of a precomputed eigenvectors (.npy)
    - inv_dict['deg']: boolean for local degree count
    - inv_dict['deg_fn']: the path of a precomputed triangle count (.npy)
    - inv_dict['ss1']: boolean for scan 1 statistic
    - inv_dict['cc']: boolean for clustering coefficient
    - inv_dict['mad']: boolean for maximum average degree
    - inv_dict['save_dir']: the base path where all invariants will create sub-dirs & be should be saved

  @param save: boolean for auto save or not. TODO: use this
  '''
  # Popualate inv_dict
  inv_dict = populate_inv_dict(inv_dict)


  if inv_dict['save_dir'] is None:
   inv_dict['save_dir'] = os.path.dirname(inv_dict['graph_fn'])

  if (inv_dict.has_key('G')):
    if inv_dict['G'] is not None:
      G = inv_dict['G']
  elif (inv_dict['graphsize'] == 'b' or inv_dict['graphsize'] == 'big'):
    G = loadAdjMat(inv_dict['graph_fn'], inv_dict['lcc_fn'])
    # small graphs
  else:
    G = loadAnyMat(inv_dict['graph_fn'], inv_dict['data_elem'])
    if isinstance(G, str):
      print G
      return G # Error message

  num_nodes = G.shape[0] # number of nodes

  # CC requires deg_fn and tri_fn. Load if available
  if inv_dict['cc']:
    # if either #tri or deg is undefined
    if not inv_dict['tri_fn']:
      inv_dict['tri'] = True
    if not inv_dict['deg_fn']:
      inv_dict['deg'] = True

    cc_array = np.zeros(num_nodes)

  # All invariants that require eigenvalues
  if ((inv_dict['tri'] and not inv_dict['tri_fn'])
      or (inv_dict['mad'])):
    if not inv_dict['eigvl_fn']:
      inv_dict['eig'] = True

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
  if inv_dict['eig']:
    if not (inv_dict['eigvl_fn'] or inv_dict['eigvect_fn']):
      l, u = arpack.eigs(G, k=k, which='LM') # LanczosMethod(A,0)
      print 'Time taken to calc Eigenvalues: %f secs\n' % (time() - start)
    else:
      try:
        l = np.load(inv_dict['eigvl_fn'])
        u = l = np.load(inv_dict['eigvect_fn'])
      except Exception:
        return "[IOERROR: ]Eigenvalues failed to load"

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
    eigvDir = os.path.join(inv_dict['save_dir'], "Eigen") #if eigvDir is None else eigvDir

    # Immediately write eigs to file
    inv_dict['eigvl_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
    inv_dict['eigvect_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
    createSave(inv_dict['eigvl_fn'], l.real) # eigenvalues
    createSave(inv_dict['eigvect_fn'], u) # eigenvectors
    print 'Eigenvalues and eigenvectors saved ...'

  ''' Triangle count '''
  if not inv_dict['tri_fn'] and inv_dict['tri']:
    triDir = os.path.join(inv_dict['save_dir'], "Triangle") #if triDir is None else triDir
    inv_dict['tri_fn'] = os.path.join(triDir, getBaseName(inv_dict['graph_fn']) + '_triangles.npy') # TODO HERE
    createSave(inv_dict['tri_fn'], tri_array)
    print 'Triangle Count saved ...'

  ''' Degree count'''
  if not inv_dict['deg_fn'] and inv_dict['deg']:
    degDir = os.path.join(inv_dict['save_dir'], "Degree") #if degDir is None else degDir
    inv_dict['deg_fn'] = os.path.join(degDir, getBaseName(inv_dict['graph_fn']) + '_degree.npy')
    createSave(inv_dict['deg_fn'], deg_array)
    print 'Degree saved ...'

  ''' MAD '''
  if inv_dict['mad']:
    MADdir = os.path.join(inv_dict['save_dir'], "MAD") #if MADdir is None else MADdir
    inv_dict['mad_fn'] = os.path.join(MADdir, getBaseName(inv_dict['graph_fn']) + '_mad.npy')
    createSave(inv_dict['mad_fn'], max_ave_deg)
    print 'Maximum average Degree saved ...'

  ''' Scan Statistic 1'''
  if inv_dict['ss1']:
    ss1Dir = os.path.join(inv_dict['save_dir'], "SS1") #if ss1Dir is None else ss1Dir
    inv_dict['ss1_fn'] = os.path.join(ss1Dir, getBaseName(inv_dict['graph_fn']) + '_scanstat1.npy')
    createSave(inv_dict['ss1_fn'], ss1_array) # save it
    print 'Scan 1 statistic saved ...'

  ''' Clustering coefficient '''
  if inv_dict['cc']:
    ccDir = os.path.join(inv_dict['save_dir'], "ClustCoeff") #if ccDir is None else ccDir
    inv_dict['cc_fn'] = os.path.join(ccDir, getBaseName(inv_dict['graph_fn']) + '_clustcoeff.npy')
    createSave(inv_dict['cc_fn'], cc_array) # save it
    print 'Clustering coefficient saved ...'

  ''' Global Vertices '''
  if inv_dict['ver']:
    vertDir = os.path.join(inv_dict['save_dir'], "Globals") #if vertDir is None else vertDir
    inv_dict['ver_fn'] = os.path.join(vertDir, getBaseName(inv_dict['graph_fn']) + '_numvert.npy')
    createSave(inv_dict['ver_fn'], num_nodes) # save it
    print 'Global vertices number saved ...'

  ''' Global number of edges '''
  if inv_dict['edge']:
    edgeDir = os.path.join(inv_dict['save_dir'], "Globals") #if edgeDir is None else edgeDir
    inv_dict['edge_fn'] = os.path.join(edgeDir, getBaseName(inv_dict['graph_fn']) + '_numedges.npy')
    createSave(inv_dict['edge_fn'], edge_count) # save it
    print 'Global edge number saved ...'

  #if test: # bench test
  #  tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_triangles.npy')
  #  eigvl_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
  #  eigvect_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
  #  MAD_fn = os.path.join('bench', str(G.shape[0]), getBaseName(inv_dict['graph_fn']) + '_MAD.npy')

  return inv_dict # TODO: Fix code this breaks. Originally was [tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn]

def populate_inv_dict(arg):

  fns = ['ss1_fn', 'tri_fn', 'deg_fn', 'ss2_fn', 'apl_fn', 'ver_fn',
          'mad_fn', 'gdia_fn', 'cc_fn', 'eigvl_fn', 'eigvect_fn', 'edge_fn']
  invs = ['ss1', 'tri', 'deg', 'ss2', 'apl', 'ver', 'eig',
          'mad', 'gdia', 'cc', 'eigvl', 'eigvect', 'edge']

  data = ['data_elem', 'k']
  if not isinstance(arg, dict):
    print "[ERROR]: argument to compute method must be of type dict"

  # Add filenames
  for fn in fns:
    if not arg.has_key(fn):
      arg[fn] = None

  # Add invariants
  for inv in invs:
    if not arg.has_key(inv):
      arg[inv] = None

  # Add auxiliary data
  for dat in data:
    if not arg.has_key(dat):
      arg[dat] = None

  return arg




if __name__ == '__main__':
  print 'This file is not to be called directly. Use helpers'
