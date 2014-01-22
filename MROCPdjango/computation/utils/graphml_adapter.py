#!/usr/bin/python

# graphml_adapter.py
# Created by Disa Mhembere on 2014-01-06.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# File performs conversion to and from scipy.sparse matrices to graphml and back

import argparse
import os
import re

__weight__=True # If the graph is weighted this will be set

def csc_to_graphml(g, is_weighted=True, desikan=False, is_directed=False, save_fn="default_name.graphml", is_tri=False, test=False):
  """
  Convert a csc graph to graphml format for writing to disk

  Positional arguments:
  ====================
  g - the csc graph

  Optional arguments:
  ===================
  is_weighted - is the graph weighted. Type: boolean.
  desikan - use the desikan mapping to label nodes. Type: boolean
  is_directed - is g symmetric ? Type: boolean
  save_fn - file name to use when saving. Type: boolean
  is_tri - is the adjacency mat upper or lower triangular. Type: boolean
  test - are we running a test. Type: boolean
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
  if desikan:
    import desikan

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

    if desikan:
      s += "  "*(tabs+1)+"<data key=\"v_region\">\"%s\"</data>\n" % (desikan.des_map.get(node, "Undefined"))

    s += "  "*tabs+"</node>\n"
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

def graphml_to_csc(fh):
  """
  Take the filehandle of a graphml formatted graph written to disk and convert to
  scipy.sparse.csc.matrix

  *Cannot account for any node attributes*
  *CAN ONLY account for edge weight attributes*
  *All other attributes are ignored if any*

  Positional arguments:
  =====================
  fh - the file handle to the graphml file
  """

  from scipy.sparse.lil import lil_matrix
  from scipy.sparse.csc import csc_matrix

  print "Processing nodes ..."
  # Assume all header stuff is ok
  while True: # Infinite loop
    pos = fh.tell()
    line = fh.readline().replace(" ", "").strip() # remove if inefficient

    if line.startswith("<node"):
      node_pos = pos # May be last node so take position

    if line.startswith("<edge"): # Wait for edges to begin
      break

  fh.seek(node_pos)
  print "Getting number of nodes ..."
  # Get number of nodes
  node_lines = fh.readline().replace(" ", "").strip()
  while not node_lines.endswith("</node>"):
    node_lines += fh.readline().replace(" ", "").strip()

  try:
    NUM_NODES = int(re.search("(?<=id=['\"]n)\d+", node_lines).group(0))+1 # +1 for 0-based indexing
  except Exception, msg:
    print "Cannot determine number of nodes from input file. Check graphml <node> syntax"

  # Got the nodes
  g = lil_matrix((NUM_NODES, NUM_NODES))

  # Put back file handle iterator
  fh.seek(pos)

  print "Getting edges ..."
  line = ""
  while True:
    line += fh.readline().replace(" ", "").strip() # remove if inefficient

    if line.endswith("</edge>"):
      edge = get_edge(line)
      g[edge[0], edge[1]] = edge[2] # Naive i.e slow. TODO: Optimize
      line = ""

    elif line.endswith("</graphml>"):
      break

  return csc_matrix(g) # Convert to CSC first

def get_edge(st):
  """
  Given a string I need to extract src, dest, weight (if available)
  No other edge attributes are representable

  Positional Args:
  ===============
  st - the string
  """
  global __weight__
  src = int(re.search("(?<=source=[\"']n)\d+", st).group())
  dest = int(re.search("(?<=target=[\"']n)\d+", st).group())

  if __weight__:
    weight = re.search("(?<=weight[\"']>)[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", st)
    if not weight:
      __weight__ = False # Only done once
    else:
      return [src, dest, float(weight.group())]
  return [src, dest, 1]

def readtest(fn):
  """
  Read Test function ran with -T flag

  Positional Args:
  ===============
  fn - filename of the of test graph
  """
  g = graphml_to_csc(open(fn, "rb"))
  print g.todense()
  print "Test complete ..."

def writetest(desikan):
  """
  Write Test function ran with -t flag

  Positional Args:
  ===============
  desikan - use the desikan mapping?
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

  src = csc_to_graphml(g, test=True, desikan=desikan)
  print "Test complete ..."
  print src

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the graph to read from disk. *Must be scipy.sparse.csc.csc_matrix or graphml format. If running test use any dummy name e.g '_'")
  parser.add_argument("-l", "--load", action="store_true", help="If we should load the file from disk")
  parser.add_argument("-p", "--dump", action="store_true", help="If we should write a graphml graph to disk")

  parser.add_argument("-w", "--weighted", action="store_true", help="Pass flag if the graph is weighted")
  parser.add_argument("-k", "--desikan", action="store_true", help="Use Desikan mapping for nodes")
  parser.add_argument("-r", "--directed", action="store_true", help="Pass flag if the graph is directed")
  parser.add_argument("-f", "--save_fn", action="store", default="default_name.graphml", help="Save file name")
  parser.add_argument("-g", "--triangular", action="store_true", help="Pass flag if the graph is triangular (upper/lower)")
  parser.add_argument("-d", "--data_elem", action="store", default=None, help="The name of the data element key in the dict.")
  parser.add_argument("-n", "--num_procs", action="store", default=None, help="STUB: The number of processors to use when converting") # TODO: CODEME

  parser.add_argument("-t", "--writetest", action="store_true", help="Run write graph from csc test only!")
  parser.add_argument("-T", "--readtest", action="store_true", help="Run read graphml to csc test only!")

  result = parser.parse_args()

  if result.readtest:
    readtest(result.graph_fn)
    exit(1)

  if result.writetest:
    writetest(result.desikan)
    exit(1)

  from time import time
  from loadAdjMatrix import loadAnyMat

  st = time()
  g = loadAnyMat(result.graph_fn, result.data_elem)

  if result.dump:
    csc_to_graphml(g, result.weighted, result.desikan, result.directed, result.save_fn, result.triangular)

  if result.load:
    graphml_to_csc(open(result.graph_fn, "rb"))

  print "Total time for conversion %.4f sec" % (time()-st)

if __name__ == "__main__":
  main()
