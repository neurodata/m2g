#!/usr/bin/python

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
#

# r_utils.py
# Created by Disa Mhembere on 2014-01-21.
# Email: disa@jhu.edu

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