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
#

# r_utils.py
# Created by Disa Mhembere on 2014-01-21.
# Email: disa@jhu.edu

import rpy2.robjects as robjects
from rpy2.rinterface import NULL
from rpy2.robjects.vectors import StrVector

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

    # =========== Graph, Node, Attr ============= #
def r_igraph_set_vertex_attr(g, attr_name, value, index=NULL, is_str=False):
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
    fn <- function(g, value, index){
      if (!is.null(index)) {
        V(g)[index]$%s <- value
      } else {
        V(g)$%s <- value
      }
      g
    }
    """ % (attr_name, attr_name))
  if is_str:
    return set_vert_attr(g, robjects.vectors.StrVector(value), index)
  return set_vert_attr(g, value, index)

def r_igraph_set_graph_attribute(g, attr_name, value):
  """
  Set/Add an igraph graph attribute in R.

  g - the R igraph object
  attr_name - the name of the vetex attribute I want to add. Type: string
  value - the R FloatVector containing the values to be added as attribute
  """

  set_graph_attr = robjects.r("""
  require(igraph)
  fn <- function(g, value){
  g$%s <- value
  g
  }
  """ % attr_name)

  return set_graph_attr(g, value)

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

def r_create_test_graph(nodes=5, edges=7):

  ctg = robjects.r("""
  require(igraph)
  fn <- function(){
  g <- erdos.renyi.game(%d, %d, type="gnm", directed=FALSE)
  }
  """ % (nodes, edges))

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
