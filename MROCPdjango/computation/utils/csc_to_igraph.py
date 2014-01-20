#!/usr/bin/python

# csc_to_igraph.py
# Created by Disa Mhembere on 2013-12-31.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

# Provide ability to convert a csc matrix in MAT format to an igraph.Graph object and save

import argparse
from scipy.sparse.csc import csc_matrix
import scipy.io as sio
import igraph
from loadAdjMatrix import loadAnyMat
from multiprocessing import Pool
from scipy.sparse import triu
from csc_matrix2 import csc_matrix2
from time import time
import os

g = None # csc global

def csc_to_igraph(cscg, save=False, fn="igraph_graph", num_procs=None):
  """
  TODO: DM
  """
  assert isinstance(cscg, csc_matrix), "Arg1 'g' must be a Scipy Sparse CSC Matrix"
  global g
  g = cscg

  print "Converting CSC to upper triangular ..."
  g = triu(g, k=0)

  print "Creating igraph from csc_matrix object ..."

  TOTAL_NODES = g.shape[0]

  ig = igraph.Graph(n=g.shape[0], directed=False) # **Note: Always undirected

  # Iterate through all non-zero edged nodes and add to list for the upper triangular of the matrix
  print "Parallel get of edges from adjacency matrix ..."
  pp = Pool(num_procs)
  g = csc_matrix2(g)
  all_new_edges = pp.map(get_edges, g) # Should return a list of np.arrays containing edges I want to add
  pp.close(); pp.join()

  # Make 2-tuple with node_id and all_non_zero entries
  print "Zipping node id its edge list ..."
  ids_edges = zip(range(TOTAL_NODES), all_new_edges) # get e.g. [ (0, [1,2,6]), (1, [2,5,8]), ... ] i.e. (node_id, [non_zero_elems])

  # Create the igraph needed (id1, id2) format for adding multiple edges
  print "Creating lists of tuple pairs ..."
  del all_new_edges
  pp = Pool(num_procs)
  edge_tups = pp.map(create_pairs, ids_edges) # Should return a list of lists, each containing 2-tuples
  pp.close(); pp.join()

  del ids_edges

  print "Serially appending to edge list ..."
  edges = []
  for node_id, l in enumerate(edge_tups):
    edges.extend(l)

    if node_id % 500 == 0:
      print "Processing node %d / %d" % (node_id, TOTAL_NODES)

  print "Adding edges to igraph object ..."
  ig += edges

  print "All igraph edges added!"

  if save:
    print "Saving to igraph graphml file format..."
    if not os.path.splitext(fn)[1] == ".graphml": fn = fn+".graphml"
    igraph.write(ig, fn, format="graphml")
    print "\nigraph saved as %s ... \nDone!" % os.path.abspath(fn)

  return ig

def create_pairs(id_edges):
  """
  Create (id1,id2) pairs to be used to add to igraph graph.
  Used in parallel mapping operations.

  positional arguments:
  =====================
  id_edges - the
  """
  return zip([id_edges[0]]*id_edges[1].shape[0], id_edges[1])

def get_edges(node):
  """
  Returns the edgelist for particular node (index of the adjacency matrix)
  Used in parallel mapping operations.

  positional arguments:
  =====================
  node - a single row of a csc matrix

  """
  return node.nonzero()[1]

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the igraph to read from disk. *Must be graphml format!")
  parser.add_argument("-s", "--save", action="store_true", help="Save conversion to disk")
  parser.add_argument("-f", "--save_fn", action="store", default="csc_matlab", help="Save file name")
  parser.add_argument("-d", "--data_elem", action="store", default=None, help="The name of the data element key in the dict.")
  parser.add_argument("-n", "--num_procs", action="store", default=None, help="The number of processors to use when converting")

  parser.add_argument("-t", "--test", action="store_true", help="Run test only!")
  result = parser.parse_args()

  if result.test:
    test()
    exit(1)

  st = time()
  g = loadAnyMat(result.graph_fn, result.data_elem)
  csc_to_igraph(g, result.save, result.save_fn, result.num_procs)

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

  g = csc_to_igraph(g)
  print "Test complete ..."
  print g.get_adjacency()

if __name__ == "__main__":
  main()
