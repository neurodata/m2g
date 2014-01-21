#!/usr/bin/python

# r_utils.py
# Created by Disa Mhembere on 2014-01-21.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import rpy2.robjects as robjects

def r_igraph_load_graph(fn, gformat="graphml"):
  """
  Load a graph from disk to an igraph object in R

  Positional arguments
  ====================
  fn - the file name on disk
  gformat - the format to read from disk. Default: graphml

  Returns
  =======
  An R igraph
  """
  get_graph = robjects.r("""
        require(igraph)
        fn <- function(fn, gformat){
          igraph::read.graph(fn, format=gformat)
       } """)

  return get_graph(fn, gformat)

def r_igraph_get_adjacency(g):
  """
  Get the adjacency matrix for a graph g

  Positional arguments
  ====================
  g - an R igraph

  Returns
  =======
  A sparse igraph adjacency matrix
  """
  get_adj = robjects.r("""
        require(igraph)
        fn <- function(g){
          igraph::get.adjacency(g)
       } """)

  return get_adj(g)