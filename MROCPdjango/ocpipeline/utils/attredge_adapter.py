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
import igraph
import os
from time import time
from collections import defaultdict
import pdb

def strip_string(word):
  return word.strip()

def get_edge(line, edge_dir=None):
  orig = line
  line = map(strip_string, line.split(","))

  # try to cast all values to int
  try:
    line = map(int , line)
    #print "Warning: Assuming all attributes are of type 'int'"
  except:
    pass

  if edge_dir == -1:
    tmp = int(line[0])
    line[0] = int(line[1])
    line[1] = tmp
  else: # edge_dir == 1:
    line[0] = int(line[0])
    line[1] = int(line[1])
  #else:
  #  print "No idea how to deal with undirected right now"
  return line

def attredge_to_igraph(gfn):
  f = open(gfn, "rb")
  line = f.readline()
  comm = line[:1]
  header = map(strip_string, line[1:].split(","))
  assert comm == "#", "First line must be a comment with attribute description .."

  attributes = map(strip_string, header[2:])
  print "There are %d attributes in the graph: %s" % (len(attributes), attributes)
  try:
    directed = attributes.index("direction")
  except:
    directed = None
    print "Graph is undirected ..."

  # idx = 0 => edge, idx = 1 => synapse_id, idx = 2 => direction
  # Can't shortcut ([]*value) this becuase it does a deep copy
  edges = [[]]
  for attr_idx in xrange(len(attributes)):
    edges.append([])

  max_node = 0

  #import pdb; pdb.set_trace() # TODO
  #if not line.lstrip().startswith("#"):
  while (True):
    line = f.readline()
    if not line: break

    #if line.lstrip().startswith("#"):


    if not line.isspace():
      edge = get_edge(line, directed)
      gnode = max(edge[0],edge[1])
      if gnode > max_node: max_node = gnode

      edges[0].append((edge[0], edge[1]))

      for attr_idx in xrange(len(attributes)):
        edges[1+attr_idx].append(edge[2+attr_idx])

  ig = igraph.Graph(max_node+1, directed=True) # Always assume directed

  start = time()
  print "Adding %d edges to the graph ..." % len(edges[0])
  ig += edges[0]
  print "Completed adding edges in %.3f sec" % (time() - start)

  start = time()
  # TODO: Deal with direction
  for attr_idx, attr in enumerate(attributes):
    print "Adding attribute '%s' to the graph ..." % attr
    ig.es[attr] = edges[attr_idx+1] # +2 accounts for src, target

  return ig

def attredge_to_graphml(gfn):
  pass

def main():
  parser = argparse.ArgumentParser(description="Convert an attributed \
      edgelist to an igraph object")

  parser.add_argument("fn", action="store", help="Edgelist filename")
  result = parser.parse_args()
  ig = attredge_to_igraph(result.fn)
  print ig.summary()

def test():
  pass

if __name__ == "__main__":
  main()
