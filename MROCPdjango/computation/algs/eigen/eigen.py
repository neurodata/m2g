#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# eigen.py
# Created by Disa Mhembere on 2014-08-03.
# Email: disa@jhu.edu

import os
from computation.utils.file_util import createSave
import rpy2.robjects as robjects
from computation.utils.r_utils import r_igraph_set_vertex_attr
from computation.utils.r_utils import r_igraph_set_graph_attribute
from computation.utils.r_utils import r_igraph_vcount

gl_eigvects = None # global eigenvectors used for fast mapping

def r_igraph_eigs(g, k, return_eigs=False, save_fn=None, real=True, lcc=False):
  """
  Eigen spectral decomposition. Compute the top-k eigen pairs.

  Positional arguments
  ====================
  @param g: The igraph graph loaded via Rpy2 i.e. an R object
  @param k: the number of eigenpairs to compute. Must be < # nodes - 2

  @param return_eigs:  boolean on whether to just return the eigenpairs or the whole graph
  @param save_fn:  must an 2 item list/tuple with 2 names OR None
  @param real: Compute only the real part
  @param lcc: use the largest connected component only

  @return: A graph with eigs as graph attributes OR actual eigenpairs
  """

  esd = robjects.r("""
  require(igraph)
  options(digits=2) # 3 decimal places
  fn <- function(g, nev, real=FALSE, lcc=FALSE){

    eig.vs <- 1:vcount(g) # at beginning
    if (lcc) {
    cat("Computing clusters ...\n")
    cl <- clusters(g) # Get clustering
    eig.vs <- which(cl$membership == which.max(cl$csize)) # get lcc vertices
    cat("Building LCC with", length(eig.vs), "vertices...\n")
    g <- induced.subgraph(g, eig.vs)
    }

    ncv <- if (nev + 50 < vcount(g)) (nev + 50) else vcount(g)
    M <- get.adjacency(g, sparse=TRUE)

    mv_mult <- function(x, extra=NULL) {
      as.vector(M %*% x) }

    cat("Computing eigs ...\n")
    eig <- arpack(mv_mult, options=list(n=vcount(g), nev=nev, ncv=ncv,  which="LM", maxiter=100))
    rm(g, M)
    cat("Taking the real parts\n")
    list((lapply(list(eig$values, t(eig$vectors)), Re)), eig.vs)# return [eigvals, eigvects, vertex.indicies] real parts only
  }
  """) # A list with [0]=eigenvalues and [1]=eigenvectors. If an eigensolver error occurs then None

  eigs = None
  vcount = r_igraph_vcount(g, False)
  nev = k if k < (vcount - 2) else (vcount-3)

  try:
    eigs = esd(g, nev, real, lcc)
  except Exception, msg:
    print msg
    return g # *Note premature exit*

  if return_eigs: return eigs # used for MAD

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn[0], eigs[0][0]) # eigenvalues
    createSave(save_fn[1], eigs[0][1]) # eigenvectors
    print "Eigenvalues saved as %s ..." % save_fn[0]
    print "eigenvectors ssaved as %s ..." % save_fn[1]
  else:

    global gl_eigvects
    gl_eigvects = eigs[0][1]

    print "Setting eigenvalues as graph attr ..."
    g = r_igraph_set_graph_attribute(g, "eigvals", "["+", ".join(map(cut, (eigs[0][0])))+"]") # Return a comma separated string

    eig_idx = eigs[1]
    print "Mapping eigenvectors ..."
    eigvects = map(get_str_eigvects, [(idx, idx+nev) for idx in xrange(0, ((len(eigs[1]))*nev), nev)])
    del eigs

    print "Setting eigenvectors as vertex attr ..."
    g = r_igraph_set_vertex_attr(g, "latent_pos", value=eigvects, index=eig_idx, is_str=True) # Could not create char sequences only lists :-/
    print "Eigenvalue computation not saved to disk. Eigen-pairs added as graph attributes ...."

  return g

def get_str_eigvects(idx):
  """
  Used for mapping to get eigenvectors that correspond to each vertex of the graph

  @param idx: a 2-tuple that gives the indexes of the eigenvector 1-d flattened matrix that correspond
  to the particular vertex

  @return: A vector i.e the eigenvector (latent position) for that vertex cast to a string
  """
  global gl_eigvects
  return "["+", ".join(map(cut, (gl_eigvects[idx[0]:idx[1]])))+"]"

def cut(num):
  """
  Shorten the format of a number to 2 decimal places plus exponent

  @param num: the number to be shorten
  """
  return "{0:.2e}".format(num)
