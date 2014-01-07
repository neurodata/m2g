#!/usr/bin/python

# convert_to_graphml.py
# Created by Disa Mhembere on 2014-01-06.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
import os
import pdb

def csc_to_graphml(g, is_weighted=True, desikan=None, is_directed=False, save_fn=None, is_tri=False):
  """
  g - the csc graph
  """
  tabs = 2 # How many tabs on append

  src = """
<?xml version="1.0" encoding="UTF-8"?>
  <graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <!-- Created by script: %s -->
    """ % __file__

  # Do we have desikan labels ?
  if desikan is not None:
    src = append(src, "<key id=\"v_region\" for=\"node\" attr.name=\"region\" attr.type=\"string\"/>", 2) # Desikan vertex attr called v_region
    tabs = 3
  
  # Is our graph weighted ?
  if is_weighted:
    src = append(src, "<key id=\"e_weight\" for=\"edge\" attr.name=\"weight\" attr.type=\"double\"/>", 2) # Desikan vertex attr called v_region
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
      src += "\n    <graph id=\"G\" edgedefault=\"undirected\">"

  for node in xrange(g.shape[0]):
    s = "<node id=\"n%d\">" % node
    s = append(s, "</node>", tabs)
    #s = "<node id=\"n%d\">\n\t\t</node>" % node

    if desikan is not None: 
      s = append(s, "<data key=\"v_region\">%s </data>" % (desikan[node]), tabs+1)
    src = append(src, s, tabs)

  print "Adding edges to graph ..."
  # Get all edge data
  nodes_from, nodes_to = g.nonzero()
  data = g.data
  del g # free some mem

  for idx in xrange(nodes_from.shape[0]): # Only the edges that exist
    src = append(src, "<edge source=\"n%d\" target=\"n%d\">" % (nodes_from[idx], nodes_to[idx]), tabs)
    if is_weighted:
      src = append(src, "<data key=\"e_weight\">%d</data>" % data[idx], tabs+1) 
    src = append(src, "</edge>", tabs)
  src = append(src, "</graph>\n</graphml>", 1)

  if save_fn:
    f = open(save_fn if os.path.splitext(save_fn)[1] == ".graphml" else save_fn+".graphml", "wb")
    f.write(src)
    f.close
  return src

class Desikan(object):
  def __init__(self, fn, g):
    pass

  
def append(src, s, tabs=2):
  return src+"\n"+"  "*tabs+s

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

  src = csc_to_graphml(g)
  print "Test complete ..."
  print src

def main():
  parser = argparse.ArgumentParser(description="Convert an igraph to a csc object")
  parser.add_argument("graph_fn", action="store", help="The name of the igraph to read from disk. *Must be gml format!")
  parser.add_argument("-k", "--desikan_key", action="store", help="Desikan key file name")
  parser.add_argument("-f", "--save_fn", action="store", default="csc_matlab", help="Save file name")
  parser.add_argument("-d", "--data_elem", action="store", default=None, help="The name of the data element key in the dict.")
  parser.add_argument("-n", "--num_procs", action="store", default=None, help="The number of processors to use when converting")

  parser.add_argument("-t", "--test", action="store_true", help="Run test only!")
  result = parser.parse_args()

  if result.test:
    test()
    exit(1)
  
  #st = time()
  #g = loadAnyMat(result.graph_fn, result.data_elem)
  #csc_to_graphml (g, result.save, result.save_fn, result.num_procs)
  
  #print "Total time for conversion %.4f sec" % (time()-st)

if __name__ == "__main__":
  main()
