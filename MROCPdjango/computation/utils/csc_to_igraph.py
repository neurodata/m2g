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

# csc_to_igraph.py
# Created by Disa Mhembere on 2013-12-31.
# Email: disa@jhu.edu

# Provide ability to convert a csc matrix in MAT format to an igraph.Graph object and save

import argparse
from scipy.sparse.csc import csc_matrix
import igraph
from file_util import loadAnyMat
from time import time
import os

def csc_to_igraph(g):
  """
  Get an igraph python representation of an adjacency matrix given
  by a sparse csc matrix

  Positional arguments:
  ====================
  g - the CSC graph

  Returns:
  =======
  A python igraph
  """
  assert isinstance(g, csc_matrix), "Arg1 'g' must be a Scipy Sparse CSC Matrix"
  ig = igraph.Graph(g.shape[0], directed=True) # Always assume directed
  nodes_from, nodes_to = g.nonzero()
  all_edges = zip(nodes_from, nodes_to)

  print "Adding edges to igraph ..."
  ig += all_edges

  # TODO - use save etc ...
  return ig

def csc_to_r_igraph(g):
  """
  Somewhat of a hack to get a GNU R representation of an igraph object from a
  python representation by reading and writing to/from a temp file

  Positional arguments:
  ====================
  g - the CSC matrix

  Returns:
  ========
  An R igraph
  """
  import tempfile
  from r_utils import r_igraph_load_graph

  t = tempfile.NamedTemporaryFile(dir="/data/pytmp")
  py_ig = csc_to_igraph(g)
  py_ig.write(t.name , format="edgelist")
  r_ig = r_igraph_load_graph(t.name, gformat="edgelist")
  t.close()
  return r_ig

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  
  result = parser.parse_args()

  st = time()
  test()
  print "Total time for conversion %.4f sec" % (time()-st)

def test():
  """
  Test function ran with -t flag
  """
  print "Running 5 node test ...."
  g = csc_matrix([
        [0, 1, 0, 0, 1],
        [1, 0, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [1, 0, 0, 0, 1]
        ])
  print "Input csc: \n", g.todense()

  print "Python igraph ...\n", csc_to_igraph(g).get_adjacency()

  from r_utils import r_igraph_get_adjacency
  print "R igraph ...\n", r_igraph_get_adjacency(csc_to_r_igraph(g))

if __name__ == "__main__":
  main()
