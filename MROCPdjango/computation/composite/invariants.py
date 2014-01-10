#!/usr/bin/python

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
import numpy as np
import igraph
import rpy2.robjects as robjects

from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils.getBaseName import getBaseName # Duplicates right now
from computation.utils import loadAdjMatrix # Duplicates right now
from computation.utils.file_util import loadAnyMat
from computation.utils.loadAdjMatrix import loadAdjMat

import argparse
from time import time
from computation.utils.file_util import createSave

def compute(inv_dict, save=True, gformat="graphml"):
  '''
  Actual function that computes invariants and saves them to a location

  positional arguments:
  =====================

  inv_dict: is a dict optinally containing any of these:
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

  optional arguments:
  ===================
  save: boolean for auto save or not. TODO: use this
  '''
  if inv_dict.get('save_dir', None) is None:
   inv_dict['save_dir'] = os.path.dirname(inv_dict['graph_fn'])

  if inv_dict.has_key('G'):
    if inv_dict['G'] is not None:
      G = inv_dict['G']
  else:
    try:
      G = r_igraph_load_graph(inv_dict['graph_fn'], gformat)
    except Exception, err_msg:
      return err_msg
  
  # Eigs and MAD
  if inv_dict.has_key('eig') or inv_dict.has_key('mad'):
    if inv_dict.has_key('eig') and inv_dict.has_key('mad'):
      eigs = "get_eigs(G)" # FIXME: STUB
      mad = "get_mad(G)" # FIXME: STUB for max of eigenvalues
    elif inv_dict.get('mad', None) is not None:
      mad = "get_mad(G)" # FIXME: STUB for max of eigenvalues
    else:
      eigs = "get_eigs(G)" # FIXME: STUB

  if inv_dict.has_key('ss1'):
    pass
  if inv_dict.has_key('tri'):
    pass
  if inv_dict.has_key('cc'):
    pass
  if inv_dict.has_key('deg'):
    pass
  if inv_dict.has_key('edge'):
    pass
  if inv_dict.has_key('ver'):
    pass

  start = time()

  # Saving invariants - FIXME may be obsolete
  if save:
    ''' Top eigenvalues & eigenvectors '''
    if not inv_dict['eigvl_fn'] and inv_dict['eig'] :
      eigvDir = os.path.join(inv_dict['save_dir'], "Eigen") #if eigvDir is None else eigvDir

      # Immediately write eigs to file
      inv_dict['eigvl_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvl.npy')
      inv_dict['eigvect_fn'] = os.path.join(eigvDir, getBaseName(inv_dict['graph_fn']) + '_eigvect.npy')
      createSave(inv_dict['eigvl_fn'], l.real) # eigenvalues
      createSave(inv_dict['eigvect_fn'], u) # eigenvectors
      print 'Eigenvalues and eigenvectors saved as ' + inv_dict['eigvect_fn']

    ''' Triangle count '''
    if not inv_dict['tri_fn'] and inv_dict['tri']:
      triDir = os.path.join(inv_dict['save_dir'], "Triangle") #if triDir is None else triDir
      inv_dict['tri_fn'] = os.path.join(triDir, getBaseName(inv_dict['graph_fn']) + '_triangles.npy')
      createSave(inv_dict['tri_fn'], tri_array)
      print 'Triangle Count saved as ' + inv_dict['tri_fn']

    ''' Degree count'''
    if not inv_dict['deg_fn'] and inv_dict['deg']:
      degDir = os.path.join(inv_dict['save_dir'], "Degree") #if degDir is None else degDir
      inv_dict['deg_fn'] = os.path.join(degDir, getBaseName(inv_dict['graph_fn']) + '_degree.npy')
      createSave(inv_dict['deg_fn'], deg_array)
      print 'Degree saved as ' + inv_dict['deg_fn']

    ''' MAD '''
    if inv_dict['mad']:
      MADdir = os.path.join(inv_dict['save_dir'], "MAD") #if MADdir is None else MADdir
      inv_dict['mad_fn'] = os.path.join(MADdir, getBaseName(inv_dict['graph_fn']) + '_mad.npy')
      createSave(inv_dict['mad_fn'], max_ave_deg)
      print 'Maximum average Degree saved as ' + inv_dict['mad_fn']

    ''' Scan Statistic 1'''
    if inv_dict['ss1']:
      ss1Dir = os.path.join(inv_dict['save_dir'], "SS1") #if ss1Dir is None else ss1Dir
      inv_dict['ss1_fn'] = os.path.join(ss1Dir, getBaseName(inv_dict['graph_fn']) + '_scanstat1.npy')
      createSave(inv_dict['ss1_fn'], ss1_array) # save it
      print 'Scan 1 statistic saved as ' + inv_dict['ss1_fn']

    ''' Clustering coefficient '''
    if inv_dict['cc']:
      ccDir = os.path.join(inv_dict['save_dir'], "ClustCoeff") #if ccDir is None else ccDir
      inv_dict['cc_fn'] = os.path.join(ccDir, getBaseName(inv_dict['graph_fn']) + '_clustcoeff.npy')
      createSave(inv_dict['cc_fn'], cc_array) # save it
      print 'Clustering coefficient saved as ' + inv_dict['cc_fn']

    ''' Global Vertices '''
    if inv_dict['ver']:
      vertDir = os.path.join(inv_dict['save_dir'], "Globals") #if vertDir is None else vertDir
      inv_dict['ver_fn'] = os.path.join(vertDir, getBaseName(inv_dict['graph_fn']) + '_numvert.npy')
      createSave(inv_dict['ver_fn'], num_nodes) # save it
      print 'Global vertices number saved as ' + inv_dict['ver_fn']

    ''' Global number of edges '''
    if inv_dict['edge']:
      edgeDir = os.path.join(inv_dict['save_dir'], "Globals") #if edgeDir is None else edgeDir
      inv_dict['edge_fn'] = os.path.join(edgeDir, getBaseName(inv_dict['graph_fn']) + '_numedges.npy')
      createSave(inv_dict['edge_fn'], edge_count) # save it
      print 'Global edge number saved as ' + inv_dict['edge_fn']

  return inv_dict

# ====================  Rpy2 Area ===================== #

def r_igraph_load_graph(fn, gformat="graphml"):
  """
  Load a graph from disk to an igraph object in R

  fn - the file name on disk
  gformat - the format to read from disk. Default: graphml
  """
  get_graph = robjects.r(""" 
        require(igraph)
        rg <- function(fn, gformat){
          igraph::read.graph(fn, format=gformat)
       } """)

  return get_graph(fn, gformat)

def ss1(g, save_fn=None):
  """
  Compute the scan statistic 1 of graph g and save as necessary

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Optional arguments
  ==================
  save_fn - the filename you want to use to save it. If not provided
  the graph adds a scan_stat1 attribute to all nodes and returns.
  """
  if not save_fn:
    save_fn = robjects.r("NULL")

  ss1 = robjects.r("""
  require(igraph)
  ss1 <- function(g, save_fn){
    scan1vector <- igraph::scan1(g)
  }
  """)
  ss1vector = ss1(g, save_fn)

  if save_fn:
    np.save(save_fn, ss1vector) # TODO: Clean input for programmatic access
  else:
    g = r_add_attr(g, ss1vector, "scan_stat1")  # Add ss1 to graph. Attribute name may need to change

  return g # return so we can use for other attributes

def deg(g, save_fn=None):
  """
  """
  pass

def cc(g, save_fn=None):
  """
  """
  pass

def tri(g, save_fn=None):
  """
  """
  pass

def eigs(g, save_fn=None):
  """
  """
  pass

def r_set_vetex_attr(g, attr_name, value):
  """
  Set/Add an R vertex attribute to an R igraph object.
  The vertex length must equal the number of nodes.

  Positional arguments:
  =====================
  g - the R igraph object
  attr_name - the name of the vetex attribute I want to add. Type: string
  value - the R FloatVector containing the values to be added as attribute
  """

  set_vert_attr = robjects.r("""
  require(igraph)
  sva <- function(g, attr_name, value){
  set.vertex.attribute(g, attr_name, value)
  }
  """)
  return set_vert_attr(g, attr_name, value)


if __name__ == '__main__':

  # Added for -h flag
  parser = argparse.ArgumentParser(description="Script to run selected invariants")
  result =  parser.parse_args()

  inv_dict = {}
  inv_dict["graph_fn"] = "/data/projects/disa/groundTruthSmGraph_fiber.mat"
  inv_dict["save_dir"] =  "/Users/disa/MR-connectome/MROCPdjango/computation/tests/profile_results"

  inv_dict["graphsize"] = 's'
  inv_dict["cc"] = inv_dict["ss1"] = inv_dict["tri"] = inv_dict["mad"] = True

  compute(inv_dict, save = True)

  #python -m cProfile -o profile.pstats invariants.py
