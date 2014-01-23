#!/usr/bin/python

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
from math import ceil
import numpy as np
import argparse
from time import time

import igraph
import rpy2.robjects as robjects
from rpy2.rinterface import NULL
from rpy2.robjects.vectors import StrVector
import scipy.sparse.linalg.eigen.arpack as arpack

from computation.utils.getBaseName import getBaseName
from computation.utils.file_util import createSave, loadAnyMat
from computation.utils.igraph_attributes import r_igraph_get_attr
from computation.utils.csc_to_igraph import csc_to_r_igraph
from computation.utils.r_utils import r_igraph_load_graph

gl_eigvects = None # global eigenvectors used for fast mapping

def compute(inv_dict, sep_save=True, gformat="graphml"):
  """
  Actual function that computes invariants and saves them to a location

  positional arguments:
  =====================

  inv_dict: is a dict that must contain:
    - inv_dict["graph_fn"]

  inv_dict: optional arguments:
    - inv_dict["edge"]: boolean for global edge count
    - inv_dict["ver"]: boolean for global vertex number
    - inv_dict["tri"]: boolean for local triangle count
    - inv_dict["eig"]: boolean for eigenvalues and eigenvectors
    - inv_dict["deg"]: boolean for local degree count
    - inv_dict["ss1"]: boolean for scan 1 statistic
    - inv_dict["cc"]: boolean for clustering coefficient
    - inv_dict["mad"]: boolean for maximum average degree
    - inv_dict["k]: the  number of eigenvalues to compute
    - inv_dict["save_dir"]: the base path where all invariants will create sub-dirs & be should be saved

  optional arguments:
  ===================
  sep_save: boolean for auto save or not
  """

  if inv_dict.get("save_dir", None) is None:
   inv_dict["save_dir"] = os.path.join(os.path.dirname(inv_dict["graph_fn"]), "graphInvariants")

  if not os.path.exists(inv_dict["save_dir"]): os.makedirs(inv_dict["save_dir"])

  if inv_dict.has_key("G"):
    if inv_dict["G"] is not None:
      G = inv_dict["G"]
  else:
    try:
      if gformat in ["edgelist", "pajek", "ncol", "lgl", "graphml", "dimacs", "gml", "dot", "leda"]: #  All igraph supported formats
        G = r_igraph_load_graph(inv_dict["graph_fn"], gformat)
      elif gformat == "mat":
        G = csc_to_r_igraph(loadAnyMat(inv_dict['graph_fn']))

        gformat = "graphml" # change graph format to something igraph can write

      if isinstance(G, str):
        return G # There was a loading error
    except Exception, err_msg:
      return err_msg

  #============================ Call to invariants ============================#
  start = time()

  if inv_dict.get("eig", None) is not None:
    inv_dict["k"] = max(50, r_igraph_vcount(G, False)-3) # Max of 50 eigenvalues
    print "Computing eigen decompositon ..."
    if sep_save:
      inv_dict["eigvl_fn"] = os.path.join(inv_dict["save_dir"], "Eigen", \
                                getBaseName(inv_dict["graph_fn"]) + "_eigvl.npy")
      inv_dict["eigvect_fn"] = os.path.join(inv_dict["save_dir"], "Eigen", \
                                getBaseName(inv_dict["graph_fn"]) + "_eigvect.npy")
      G = r_igraph_eigs(G, inv_dict['k'], save_fn=(inv_dict["eigvl_fn"], inv_dict["eigvect_fn"]))
    else: G = r_igraph_eigs(G, inv_dict['k'], save_fn=None)

  if inv_dict.get("mad", None) is not None:
    if sep_save:
      inv_dict["mad_fn"] = os.path.join(inv_dict["save_dir"], "MAD", \
                                getBaseName(inv_dict["graph_fn"]) + "_mad.npy")
    print "Computing MAD ..."
    G = r_igraph_max_ave_degree(G)

  if inv_dict.get("ss1", None) is not None:
    print "Computing Scan 1 ..."
    if sep_save:
      inv_dict["ss1_fn"] = os.path.join(inv_dict["save_dir"], "SS1", \
                                getBaseName(inv_dict["graph_fn"]) + "_scanstat1.npy")
    G = r_igraph_scan1(G, inv_dict.get("ss1_fn", None))

  if inv_dict.get("tri", None) is not None:
    print "Computring triangle count ..."
    if sep_save:
      inv_dict["tri_fn"] = os.path.join(inv_dict["save_dir"], "Triangle", \
                                getBaseName(inv_dict["graph_fn"]) + "_triangles.npy")
    G = r_igraph_triangles(G, inv_dict.get("tri_fn", None))

  if inv_dict.get("cc", None) is not None:
    print "Computing clustering coefficient .."
    if sep_save:
      inv_dict["cc_fn"] = os.path.join(inv_dict["save_dir"], "ClustCoeff",\
                                getBaseName(inv_dict["graph_fn"]) + "_clustcoeff.npy")
    G = r_igraph_clust_coeff(G, inv_dict.get("cc_fn", None))

  if inv_dict.get("deg", None) is not None:
    print "Computing degree ..."
    if sep_save:
      inv_dict["deg_fn"] = os.path.join(inv_dict["save_dir"], "Degree",\
                                getBaseName(inv_dict["graph_fn"]) + "_degree.npy")
    G = r_igraph_degree(G, inv_dict.get("deg_fn", None))

  # num edges
  if inv_dict.get("edge", None) is not None:
    print "Computing global edge count ..."
    G = r_igraph_ecount(G, True)

  # num vertices
  if inv_dict.get("ver", None) is not None:
    print "Computing global vertex count ..."
    G = r_igraph_vcount(G, True)

  print "Total invariant compute time = %.3fsec" % (time() - start)

  # Save graph with all new attrs
  inv_dict["out_graph_fn"] = os.path.join(inv_dict["save_dir"], os.path.splitext(os.path.basename(inv_dict["graph_fn"]))[0])
  if os.path.splitext(inv_dict["out_graph_fn"])[1][1:] != gformat: inv_dict["out_graph_fn"] += "."+gformat
  r_igraph_write(G, inv_dict["out_graph_fn"], gformat)

  return G, inv_dict

# ==============================  Rpy2 Area ================================== #

def r_igraph_write(g, fn, gformat="graphml"):
  """
  Save an R igraph to disk via the R interface

  fn - the file name on disk
  gformat - the format to read from disk. Default: graphml
  """
  print "Writing %s to disk ..." % fn

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
  the graph adds a scan1 attribute to all nodes and returns.
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
    g = r_igraph_set_vertex_attr(g, "scan1", ss1vector)  # Attribute name may need to change

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
  the graph adds a degree attribute to all nodes and returns.
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
  the graph adds a clustcoeff attribute to all nodes and returns.
  """

  clustcoeff = robjects.r("""
  require(igraph)
  fn <- function(g){
  igraph::transitivity(g, "local")
  }
  """)
  ccvector = clustcoeff(g)

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
  the graph adds a tri count attribute to all nodes and returns.
  """

  triangles = robjects.r("""
  require(igraph)
  fn <- function(g){
  igraph::adjacent.triangles(g)
  }
  """)
  trivector = triangles(g)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn, trivector) # TODO: Clean input for programmatic access
    print "Triangle Count saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "tri", trivector)  # Attribute name may need to change

  return g # return so we can use for other attributes

def r_igraph_eigs(g, k, return_eigs=False, save_fn=None, real=True):
  """
  Eigen spectral decomposition. Compute the top-k eigen pairs.

  Positional arguments
  ====================
  g - The igraph graph loaded via Rpy2 i.e. an R object
  k - the number of eigenpairs to compute. Must be < # nodes - 2

  Optional arguments
  ==================
  save_fn - must an 2 item list/tuple with 2 names OR None
  return_eigs - boolean on whether to just return the eigenpairs or the whole graph

  Returns
  =======

  A graph with eigs as graph attributes OR actual eigenpairs
  """

  esd = robjects.r("""
  require(igraph)
  options(digits=2) # 3 decimal places
  fn <- function(g, nev, ncv, real=FALSE){
    M <- get.adjacency(g, sparse=TRUE)

    mv_mult <- function(x, extra=NULL) {
      as.vector(M %*% x) }

    eig <- arpack(mv_mult, options=list(n=vcount(g), nev=nev, ncv=ncv,  which="LM", maxiter=500))
    lapply(list(eig$values, t(eig$vectors)), Re) # return [eigvals, eigvects] real parts only
  }
  """) # A list with [0]=eigenvalues and [1]=eigenvectors. If an eigensolver error occurs then None

  eigs = None
  vcount = r_igraph_vcount(g, False)
  nev = k if k < (vcount - 2) else (vcount-3)
  ncv = nev + 20 if (nev + 20) < vcount else vcount

  try:
    eigs = esd(g, nev, ncv, real)
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

    global gl_eigvects
    gl_eigvects = eigs[1]

    eigvects = map(get_str_eigvects, [(idx, idx+nev) for idx in xrange(0, (vcount*nev), nev)])
    g = r_igraph_set_graph_attribute(g, "eigvals", str(list(eigs[0]))) # Return a comma separated string

    #g = r_igraph_set_vertex_attr(g, "latent_pos", value=eigvects) # Could not create char sequences only lists :-/

    for node in xrange(vcount):
      g = r_igraph_set_vertex_attr(g, "latent_pos", value=eigvects[node], index="c(%d)"%(node+1)) # ** +1 for R 1-based indexing **
    print "Eigenvalue computation not saved to disk. Eigen-pairs added as graph attributes ...."

  return g

def get_str_eigvects(idx):
  """
  Used for mapping to get eigenvectors that correspond to each vertex of the graph

  Positional arguments
  ====================
  idx - a 2-tuple that gives the indexes of the eigenvector 1-d flattened matrix that correspond
  to the particular vertex

  Returns
  =======
  A vector i.e the eigenvector (latent position) for that vertex cast to a string
  """
  global gl_eigvects
  return str(list(gl_eigvects[idx[0]:idx[1]]))


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
  if mad == NULL: # Ok then compute top 1 eig ourself
    mad = r_igraph_eigs(g, 1, return_eigs=True, save_fn=None)[0]
  else:
    mad = float(mad[0].split(",")[0][1:]) # The largest eigenvalue is held at index 0

  if mad is not None:
    g = r_igraph_set_graph_attribute(g, "max_ave_degree", mad)
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
    g = r_igraph_set_graph_attribute(g, "vcount", vc)
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
    g = r_igraph_set_graph_attribute(g, "ecount", ec)
    return g # return so we can use for other attributes
  else:
    return int(ec)

    # =========== Graph, Node, Attr ============= #
def r_igraph_set_vertex_attr(g, attr_name, value, index="V(g)"):
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
  set.vertex.attribute(g, attr_name, index=%s, value=value)
  }
  """ % index)

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

def r_create_test_graph(nodes=5, edges=7):

  ctg = robjects.r("""
  require(igraph)
  fn <- function(){
  g <- erdos.renyi.game(%d, %d, type="gnm", directed=FALSE)
  }
  """ % (nodes, edges))

  return ctg()

if __name__ == "__main__":

  # Added for -h flag
  parser = argparse.ArgumentParser(description="Script to run selected invariants")
  result =  parser.parse_args()

  print "Running test ...."
  inv_dict = {}

  inv_dict["G"] = r_create_test_graph()
  inv_dict["graph_fn"] = "testgraph.graphml" # dummy

  inv_dict["eig"] = True; inv_dict["k"] = 3;
  inv_dict["cc"] = True; inv_dict["ss1"] = True;
  inv_dict["tri"] = True; inv_dict["mad"] = True;
  inv_dict["ver"] =  True; inv_dict["edge"] = True; inv_dict["deg"] = True

  g = compute(inv_dict, sep_save=False)
  #python -m cProfile -o profile.pstats invariants.py