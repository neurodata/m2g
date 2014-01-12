#!/usr/bin/python

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
import numpy as np
import igraph
import rpy2.robjects as robjects
from rpy2.rinterface import NULL

from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils.getBaseName import getBaseName # Duplicates right now
from computation.utils import loadAdjMatrix # Duplicates right now
from computation.utils.file_util import loadAnyMat
from computation.utils.loadAdjMatrix import loadAdjMat

import argparse
from time import time
from computation.utils.file_util import createSave

def compute(inv_dict, sep_save=True, gformat="graphml"):
  """
  Actual function that computes invariants and saves them to a location

  positional arguments:
  =====================

  inv_dict: is a dict optinally containing any of these:
    - inv_dict["edge"]: boolean for global edge count
    - inv_dict["ver"]: boolean for global vertex number
    - inv_dict["tri"]: boolean for local triangle count
    - inv_dict["eig"]: boolean for eigenvalues and eigenvectors
    - inv_dict["deg"]: boolean for local degree count
    - inv_dict["ss1"]: boolean for scan 1 statistic
    - inv_dict["cc"]: boolean for clustering coefficient
    - inv_dict["mad"]: boolean for maximum average degree
    - inv_dict["save_dir"]: the base path where all invariants will create sub-dirs & be should be saved

  optional arguments:
  ===================
  sep_save: boolean for auto save or not
  """
  if inv_dict.get("save_dir", None) is None:
   inv_dict["save_dir"] = os.path.dirname(inv_dict["graph_fn"])

  if inv_dict.has_key("G"):
    if inv_dict["G"] is not None:
      G = inv_dict["G"]
  else:
    try:
      G = r_igraph_load_graph(inv_dict["graph_fn"], gformat)
    except Exception, err_msg:
      return err_msg

  # Determine invariant file names if we are saving them to disk separately
  if sep_save:
    """ Top eigenvalues & eigenvectors """
    if inv_dict["eigs"]:
      eigvDir = os.path.join(inv_dict["save_dir"], "Eigen")
      inv_dict["eigvl_fn"] = os.path.join(eigvDir, getBaseName(inv_dict["graph_fn"]) + "_eigvl.npy")
      inv_dict["eigvect_fn"] = os.path.join(eigvDir, getBaseName(inv_dict["graph_fn"]) + "_eigvect.npy")

    """ Triangle count """
    if inv_dict["tri"]:
      triDir = os.path.join(inv_dict["save_dir"], "Triangle")
      inv_dict["tri_fn"] = os.path.join(triDir, getBaseName(inv_dict["graph_fn"]) + "_triangles.npy")

    """ Degree count"""
    if inv_dict["deg"]:
      degDir = os.path.join(inv_dict["save_dir"], "Degree")
      inv_dict["deg_fn"] = os.path.join(degDir, getBaseName(inv_dict["graph_fn"]) + "_degree.npy")

    """ MAD """
    if inv_dict["mad"]:
      MADdir = os.path.join(inv_dict["save_dir"], "MAD")
      inv_dict["mad_fn"] = os.path.join(MADdir, getBaseName(inv_dict["graph_fn"]) + "_mad.npy")

    """ Scan Statistic 1"""
    if inv_dict["ss1"]:
      ss1Dir = os.path.join(inv_dict["save_dir"], "SS1")
      inv_dict["ss1_fn"] = os.path.join(ss1Dir, getBaseName(inv_dict["graph_fn"]) + "_scanstat1.npy")

    """ Clustering coefficient """
    if inv_dict["cc"]:
      ccDir = os.path.join(inv_dict["save_dir"], "ClustCoeff")
      inv_dict["cc_fn"] = os.path.join(ccDir, getBaseName(inv_dict["graph_fn"]) + "_clustcoeff.npy")

  return inv_dict

  #============================ Call to invariants ============================#
  start = time()

  if inv_dict.get("eig", None) is not None:
    G = r_igraph_eigs(G, inv_dict['k'], (inv_dict["eigvl_fn"], inv_dict["eigvect_fn"]))

  if inv_dict.get("mad", None) is not None:
    G = r_igraph_max_ave_degree(G)

  if inv_dict.get("ss1", None) is not None:
    G = r_igraph_scan1(G, inv_dict["ss1_fn"])

  if inv_dict.get("tri", None) is not None:
    G = r_igraph_triangles(G, inv_dict["tri_fn"])

  if inv_dict.get("cc", None) is not None:
    G = r_igraph_clust_coeff(G, inv_dict["cc_fn"])

  if inv_dict.get("deg", None) is not None:
    G = r_igraph_degree(G, inv_dict["deg_fn"])

  # num edges
  if inv_dict.get("edge", None) is not None:
    G = r_igraph_ecount(G, True)

  # num vertices
  if inv_dict.get("ver", None) is not None:
    G = r_igraph_vcount(G, True)

  print "Total invariant compute time = %.3fsec" % (time() - start)

# ==============================  Rpy2 Area ================================== #

def r_igraph_load_graph(fn, gformat="graphml"):
  """
  Load a graph from disk to an igraph object in R

  fn - the file name on disk
  gformat - the format to read from disk. Default: graphml
  """
  get_graph = robjects.r("""
        require(igraph)
        fn <- function(fn, gformat){
          igraph::read.graph(fn, format=gformat)
       } """)

  return get_graph(fn, gformat)

def r_igraph_write(g, fn, gformat="graphml"):
  """
  Save an R igraph to disk via the R interface

  fn - the file name on disk
  gformat - the format to read from disk. Default: graphml
  """
  write_graph = robjects.r("""
        require(igraph)
        fn <- function(g, fn, gformat){
        write.graph(g, fn, format=gformat)
       } """)

  write_graph(g, fn, gformat)

def r_igraph_scan1(g, save_fn=None):
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

  scanstat1 = robjects.r("""
  require(igraph)
  fn <- function(g){
  igraph::scan1(g)
  }
  """)
  ss1vector = scanstat1(g)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(os.path.abspath(save_fn), ss1vector) # TODO: Clean input for programmatic access
    print  "Scan Statistic saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "scan_stat1", ss1vector)  # Attribute name may need to change

  return g # return so we can use for other attributes

def r_igraph_degree(g, save_fn=None):
  """
  Compute degree of graph g and save as necessary

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Optional arguments
  ==================
  save_fn - the filename you want to use to save it. If not provided
  the graph adds a scan_stat1 attribute to all nodes and returns.
  """

  deg = robjects.r("""
  require(igraph)
  fn <- function(g){
  igraph::degree(g, mode="total")
  }
  """)
  degvector = deg(g)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn, degvector) # TODO: Clean input for programmatic access
    print "Degree saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "degree", degvector)  # Attribute name may need to change

  return g # return so we can use for other attributes

def r_igraph_clust_coeff(g, save_fn=None):
  """
  Compute clustering coefficient of graph g and save as necessary

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Optional arguments
  ==================
  save_fn - the filename you want to use to save it. If not provided
  the graph adds a clustering coefficient attribute to all nodes and returns.
  """
  if not save_fn:
    save_fn = robjects.r("NULL")

  clustcoeff = robjects.r("""
  require(igraph)
  fn <- function(g, save_fn){
  igraph::transitivity(g, "local")
  }
  """)
  ccvector = clustcoeff(g, save_fn)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn, ccvector) # TODO: Clean input for programmatic access
    print "Clustering Coefficient saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "clustcoeff", ccvector)  # Attribute name may need to change

  return g # return so we can use for other attributes

def r_igraph_triangles(g, save_fn=None):
  """
  Compute local triangle count of graph g and save as necessary

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Optional arguments
  ==================
  save_fn - the filename you want to use to save it. If not provided
  the graph adds a triangle count attribute to all nodes and returns.
  """
  if not save_fn:
    save_fn = robjects.r("NULL")

  triangles = robjects.r("""
  require(igraph)
  fn <- function(g, save_fn){
  igraph::adjacent.triangles(g)
  }
  """)
  trivector = triangles(g, save_fn)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn, trivector) # TODO: Clean input for programmatic access
    print "Triangle Count saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "tri", trivector)  # Attribute name may need to change

  return g # return so we can use for other attributes

def r_igraph_eigs(g, k, save_fn=None, return_eigs=False):
  """
  Eigen spectral decomposition. Compute the top-k eigen pairs.

  Positional arguments
  ====================
  g - The igraph graph loaded via Rpy2 i.e. an R object
  k - the number of eigenpairs to compute. Must be < # nodes - 2

  Optional arguments
  ==================
  save_fn - must an 2 item list/tuple with 2 names OR None

  Returns
  =======

  A graph with eigs as graph attributes
  """

  esd = robjects.r("""
  require(igraph)
  fn <- function(g, nev, ncv){
    M <- get.adjacency(g, sparse=TRUE)

    mv_mult <- function(x, extra=NULL) {
      as.vector(M %*% x) }

    eig <- arpack(mv_mult, options=list(n=vcount(g), nev=nev, ncv=ncv,  which="LM", maxiter=500))
    list(eig$values, eig$vectors) # return [eigvals, eigvects]
  }
  """) # A list with [0]=eigenvalues and [1]=eigenvectors. If an eigensolver error occurs then None

  eigs = None
  vcount = r_igraph_vcount(g, False)
  nev = k if k < (vcount - 2) else (vcount-3)
  ncv = nev + 20 if (nev + 20) < vcount else vcount

  try:
    eigs = esd(g, nev, ncv)
  except Exception, msg:
    print msg
    return g # *Note premature exit*

  if return_eigs: return eigs # used for MAD

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn[0], eigs[0]) # eigenvalues
    createSave(save_fn[1], eigs[1]) # eigenvectors
    print "Eigenvalues saved as %s ..." % save_fn[0]
    print "eigenvectors ssaved as %s ..." % save_fn[1]
  else:
    g = r_igraph_set_graph_attribute(g, "eigvals", eigs[0])
    g = r_igraph_set_graph_attribute(g, "eigvects", eigs[1])
    print "Eigenvalue computation not saved to disk! Eigen-pairs added as graph attributes ...."

  return g

def r_igraph_max_ave_degree(g):
  """
  Compute local triangle count of graph g and save as necessary
  *Global graph attributes can only be stored in the graph*

  Positional arguments
  ====================
  g - The igraph graph loaded via Rpy2 i.e. an R object

  Optional arguments
  ==================
  save_fn - the filename you want to use to save it. If not provided

  Returns
  =======
  g - Same graph an input but with added invariant as an attribute
  """

  mad = r_igraph_get_attr(g, "eigvals", "g") # See if we already have computed eigenvalues for the graph
  if isinstance(mad, NULL): # Ok then compute top 1 eig ourself
    mad = r_igraph_eigs(g, 1, save_fn=None, return_eigs=True)
  else:
    mad = mad[0] # The largest eigenvalue is held at index 0

  if mad is not None:
    g = r_igraph_set_graph_attribute(g, "max_ave_degree", mad[0])  # Attribute name may need to change
  else: # More than likely ran out of memory
    print "Failed to estimate max ave degree because eigensolver failed ..."

  return g # return so we can use for other attributes

def r_igraph_vcount(g, set_attr=True):
  """
  Get global vertex count of graph g and add as an attribut to graph
  *Global graph attributes can only be stored in the graph*

  Positional arguments
  ====================
  g - The igraph graph loaded via Rpy2 i.e. an R object

  Returns
  =======
  g - Same graph an input but with added invariant as an attribute OR
  vc - the actual vertex count
  """
  vcount = robjects.r("""
  require(igraph)
  fn <- function(g){
  vcount(g)
  }
  """)
  vc = vcount(g)[0]
  if set_attr:
    g = r_igraph_set_graph_attribute(g, "vcount", vc)  # Attribute name may need to change
    return g # return so we can use for other attributes

  else:
    return int(vc)

def r_igraph_ecount(g, set_attr=True):
  """
  Compute local triangle count of graph g and save as necessary
  *Global graph attributes can only be stored in the graph*

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Returns
  =======
  g - Same graph an input but with added invariant as an attribute
  """
  ecount = robjects.r("""
  require(igraph)
  fn <- function(g){
  ecount(g)
  }
  """)
  ec = ecount(g)[0]
  if set_attr:
    g = r_igraph_set_graph_attribute(g, "ecount", ec)  # Attribute name may need to change
    return g # return so we can use for other attributes
  else:
    return int(ec)

    # =========== Graph, Node, Attr ============= #
def r_igraph_set_vertex_attr(g, attr_name, value):
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
  fn <- function(g, attr_name, value){
  set.vertex.attribute(g, attr_name, value=value)
  }
  """)

  return set_vert_attr(g, attr_name, value)

def r_igraph_set_graph_attribute(g, attr_name, value):
  """
  Set/Add an igraph graph attribute in R.

  g - the R igraph object
  attr_name - the name of the vetex attribute I want to add. Type: string
  value - the R FloatVector containing the values to be added as attribute
  """

  set_graph_attr = robjects.r("""
  require(igraph)
  fn <- function(g, attr_name, value){
  set.graph.attribute(g, attr_name, value=value)
  }
  """)
  return set_graph_attr(g, attr_name, value)

def r_igraph_get_attr(g, attr_name, which):
  """
  Get an igraph graph attribute in R.

  Positional arguments
  ====================
  g - the R igraph object
  attr_name - the name of the vetex attribute I want to get. Type: string
  which - "g"/"e"/"v" stand for graph, edge, vertex

  Returns
  ======
  The requested attribute

  """

  attr_dict = {"g":"graph", "e":"edge", "v":"vertex"}

  get = robjects.r("""
  require(igraph)
  fn <- function(g, attr_name){
  get.%s.attribute(g, attr_name)
  }
  """ %attr_dict.get(which, "graph")) # assume graph attr if not specified

  return get(g, attr_name)


if __name__ == "__main__":

  # Added for -h flag
  parser = argparse.ArgumentParser(description="Script to run selected invariants")
  result =  parser.parse_args()

  inv_dict = {}
  inv_dict["graph_fn"] = "/data/projects/disa/groundTruthSmGraph_fiber.mat"
  inv_dict["save_dir"] =  "/Users/disa/MR-connectome/MROCPdjango/computation/tests/profile_results"

  inv_dict["graphsize"] = "s"
  inv_dict["cc"] = inv_dict["ss1"] = inv_dict["tri"] = inv_dict["mad"] = True

  compute(inv_dict, save = True)

  #python -m cProfile -o profile.pstats invariants.py
