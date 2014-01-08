#!/usr/bin/python

# igraph_to_csc.py
# Created by Disa Mhembere on 2013-12-31.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

# Provide ability to create ER igraphs, convert igraph.Graph objects to MAT format graphs

import argparse
from scipy.sparse.csc import csc_matrix
import scipy.io as sio
import igraph
import os
import sys

def igraph_to_csc(g, save=False, fn="csc_matlab"):
  """
  Convert an igraph to scipy.sparse.csc.csc_matrix

  Positional arguments:
  =====================
  g - the igraph graph

  Optional arguments:
  ===================
  save - save file to disk
  fn - the file name to be used when writing (appendmat = True by default)
  """
  assert isinstance(g, igraph.Graph), "Arg1 'g' must be an igraph graph"
  print "Creating CSC from igraph object ..."
  gs = csc_matrix(g.get_adjacency().data) # Equiv of calling to_dense so may case MemError
  print "CSC creation complete ..."

  if save:
    print "Saving to MAT file ..."
    sio.savemat(fn, {"data":gs}, True) # save as MAT format only. No other options!
  return gs

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the igraph to read from disk. *Must be gml format!")

  parser.add_argument("-g", "--gen_graph", action="store_true", help="Generate a new ER graph")
  parser.add_argument("-n", "--num_nodes", action="store", type=int, help="The number of nodes in the ER graph")
  parser.add_argument("-p", "--probability", action="store", type=float, help="The probability of connectivity of each node to another in the graph")
  parser.add_argument("-s", "--save", action="store_true", help="Save conversion to disk")
  parser.add_argument("-f", "--save_fn", action="store", default="csc_matlab", help="Save file name")

  parser.add_argument("-t", "--test", action="store_true", help="Run test only!")

  result = parser.parse_args()

  if result.test:
    test()
    exit(1)

  if os.path.exists(result.graph_fn):
    g = igraph.read(result.graph_fn, format="gml")

  elif result.gen_graph or result.num_nodes or result.probability:
    assert (result.gen_graph and result.num_nodes and result.probability), "You must set all ER parameters i.e. n, p"
    g = igraph.Graph.Erdos_Renyi(n=result.num_nodes, p=result.probability)
    igraph.write(g, result.save_fn+".gml", format="gml")

  else:
    sys.stderr.writelines("Invalid path %s ... and all (i.e. n, p, g) ER parameters not set so no action taken. \n EXITING NOW! \n")
    exit(-1)

  igraph_to_csc(g, result.save, result.save_fn)

def test():
  """
  Test function ran with -t flag
  """
  print "Running 5 node test ...."
  g = igraph.Graph.Erdos_Renyi(n=5, p=0.3)
  g = igraph_to_csc(g)
  print "Test complete ..."
  print g.todense()

if __name__ == "__main__":
  main()