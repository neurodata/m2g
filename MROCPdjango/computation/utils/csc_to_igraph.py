#!/usr/bin/python

# csc_to_igraph.py
# Created by Disa Mhembere on 2013-12-31.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

# Provide ability to convert a csc matrix in MAT format to an igraph.Graph object and save

import argparse
from scipy.sparse.csc import csc_matrix
from scipy.sparse.lil import lil_matrix
import scipy.io as sio
import igraph
from loadAdjMatrix import loadAnyMat
from multiprocessing import Pool
from scipy.sparse import triu

class Node(object):
  def __init__(self, ):
    """
    TODO: DM
    """
    pass

def csc_to_igraph(g, save=False, fn="igraph_graph"):
  """
  TODO: DM
  """
  assert isinstance(g, csc_matrix), "Arg1 'g' must be a Scipy Sparse CSC Matrix"

  print "Converting CSC to upper triangular ..."
  g = triu(g, k=0)

  print "Creating igraph from csc_matrix object ..."

  TOTAL_NODES = g.shape[0]

  ig = igraph.Graph(n=g.shape[0], directed=False) # **Note: Always undirected

  edges = [] # List of edges

  # Iterate through all non-zero edged nodes and add to list for the upper triangular of the matrix

  #pp = Pool()
  #all_new_edges = pp.map(get_edges, g) # Should return a list of np.arrays containing edges I want to add

  for node in xrange(g.shape[0]):
    if g[node].nnz: # if we have an edge
      new_edges =  g[node].nonzero()[1]

      edges.extend(zip([0]*g[node].nonzero()[1].shape[0], g[node].nonzero()[1]))

    if TOTAL_NODES % 500 == 0:
      print "Processing node %d / %d" % (node, TOTAL_NODES)

  print "All nodes processed ...\n Adding igraph edges ..."

  ig += edges

  print "All igraph edges added ..."

  if save:
    print "Saving to igraph gml file format..."
    igraph.write(ig, fn, format="gml")

  return ig

def get_edges(node):
  """ TODO: DM """
  return node.nonzero()[1] # This assumes matrix is already in upper triangular form

def extend_list(l, edges):
  """ TODO: DM """
  l.extend(edges)

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the igraph to read from disk. *Must be gml format!")
  parser.add_argument("-s", "--save", action="store_true", help="Save conversion to disk")
  parser.add_argument("-f", "--save_fn", action="store", default="csc_matlab", help="Save file name")
  parser.add_argument("-d", "--data_elem", action="store", default=None, help="The name of the data element key in the dict.")

  parser.add_argument("-t", "--test", action="store_true", help="Run test only!")
  result = parser.parse_args()

  if result.test:
    test()
    exit(1)

  g = loadAnyMat(result.graph_fn, result.data_elem)
  igraph_to_csc(g, result.save, result.save_fn)

def test():
  """
  Test function ran with -t flag
  """
  print "Running 5 node test ...."
  g = csc_matrix([
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
        ])

  g = csc_to_igraph(g)
  print "Test complete ..."
  print g.get_adjacency()

if __name__ == "__main__":
  main()