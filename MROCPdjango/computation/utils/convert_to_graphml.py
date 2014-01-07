#!/usr/bin/python

# convert_to_graphml.py
# Created by Disa Mhembere on 2014-01-06.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
import os

def csc_to_graphml(g, is_weighted=True, desikan=None, is_directed=False, save_fn="default_name.graphml", is_tri=False, test=False):
  """
  g - the csc graph
  """
  print "Beginning graphml construction .."
  if test: test_str = ""

  tabs = 2 # How many tabs on affix to the front

  src = """<?xml version="1.0" encoding="UTF-8"?>
  <graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <!-- Created by script: %s -->\n""" % __file__

  # Do we have desikan labels ?
  if desikan is not None:
    src += "  "*2+"<key id=\"v_region\" for=\"node\" attr.name=\"region\" attr.type=\"string\"/>\n" # Desikan vertex attr called v_region
    tabs = 3
  
  # Is our graph weighted ?
  if is_weighted:
    src += "  "*2+"<key id=\"e_weight\" for=\"edge\" attr.name=\"weight\" attr.type=\"double\"/>\n" # Desikan vertex attr called v_region
    tabs = 3
  
  # Directed graph ?
  if is_directed:
    src += "\n    <graph id=\"G\" edgedefault=\"undirected\">"
  
  # Undirected graph?
  else:  # not directed so just use upper tri
    if not is_tri:
      print "Converting to upper triangular ..."
      from scipy.sparse.csc import csc_matrix
      from scipy.sparse import triu

      g = g = csc_matrix(triu(g, k=0))
      src += "\n    <graph id=\"G\" edgedefault=\"undirected\">\n"

  NUM_NODES = g.shape[0]

  if not test: f = open(save_fn if os.path.splitext(save_fn)[1] == ".graphml" else save_fn+".graphml", "wb")

  # Can be #pragma for
  for node in xrange(NUM_NODES): # Cycle through all nodes
    s = "<node id=\"n%d\">\n" % node
    s += "  "*tabs+"</node>\n"

    if desikan is not None: 
      s += "  "*(tabs+1)+"<data key=\"v_region\">%s </data>\n" % (desikan[node])

    src += "  "*tabs+s

    if node % 50000 == 0:
      print "Processing node %d / %d ..." % (node, NUM_NODES)
      if test: test_str += src
      else: f.write(src)
      src = ""
  
  del s # free mem

  print "Adding edges to graph ..."
  # Get all edge data
  nodes_from, nodes_to = g.nonzero()
  data = g.data
  del g # free some mem
  
  # Can be #pragma for
  NUM_EDGES = nodes_from.shape[0]
  for idx in xrange(NUM_EDGES): # Only the edges that exist
    src += "  "*tabs+"<edge source=\"n%d\" target=\"n%d\">\n" % (nodes_from[idx], nodes_to[idx])
    if is_weighted:
      src += "  "*(tabs+1)+"<data key=\"e_weight\">%d</data>\n" % data[idx] 
    src += "  "*tabs+"</edge>\n"

    if idx % 100000 == 0:
      print "Processing edge %d / %d ..." % (idx, NUM_EDGES)
      if test: test_str += src 
      else: f.write(src)
      src = ""
      
  src += "  </graph>\n</graphml>"
  
  if test: 
    test_str += src
    return test_str

  f.write(src)
  f.close

class Desikan(object):
  des_map = {}

  def __init__(self, g):
    pass

  def get_mapping(self, ):
    return [] # FIXME stub

def test():
  """
  Test function ran with -t flag
  """
  from scipy.sparse.csc import csc_matrix
  print "Running 5 node test ...."
  g = csc_matrix([
        [0, 1, 0, 0, 5],
        [1, 0, 3, 1, 0],
        [0, 3, 0, 1, 0],
        [0, 1, 1, 0, 0],
        [5, 0, 0, 0, 0]
        ])

  src = csc_to_graphml(g, test=True)
  print "Test complete ..."
  print src

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the graph to read from disk. *Must be scipy.sparse.csc.csc_matrix format!")
  parser.add_argument("-w", "--weighted", action="store_true", help="Pass flag if the graph is weighted")
  parser.add_argument("-k", "--desikan", action="store_true", default=None, help="Use Desikan mapping")
  parser.add_argument("-r", "--directed", action="store_true", help="Pass flag if the graph is directed")
  parser.add_argument("-f", "--save_fn", action="store", default="default_name.graphml", help="Save file name")
  parser.add_argument("-g", "--triangular", action="store_true", help="Pass flag if the graph is triangular (upper/lower)")
  parser.add_argument("-d", "--data_elem", action="store", default=None, help="The name of the data element key in the dict.")
  parser.add_argument("-n", "--num_procs", action="store", default=None, help="STUB: The number of processors to use when converting")

  parser.add_argument("-t", "--test", action="store_true", help="Run test only!")
  result = parser.parse_args()

  if result.test:
    test()
    exit(1)
  
  from time import time
  from loadAdjMatrix import loadAnyMat

  st = time()
  g = loadAnyMat(result.graph_fn, result.data_elem)

  if result.desikan:
    result.desikan = Desikan(g).get_mapping()

  csc_to_graphml(g, result.weighted, result.desikan, result.directed, result.save_fn, result.triangular)
  
  print "Total time for conversion %.4f sec" % (time()-st)

if __name__ == "__main__":
  main()
