#!/usr/bin/python

# tensorfy_graph.py
# Created by Disa Mhembere on 2014-11-25.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
import igraph_io
import os
from glob import glob
import igraph
from collections import defaultdict

GRAPH_SIZE = 70

# NOTE: Only use this script on relatively small graphs as it
#   is not optimized for memory / speed.
def make_graphml_tensor_graph(graphs):
  """
  Make a tensor graph from a series (may be just 2) of graphs.

  @param graphs: A list of fully qualified file names for graphs.
  @param output: The name of the tensor graph output.
  """
  base_graph = igraph_io.read_arbitrary(graphs[0], informat="graphml")
  
  for attr in base_graph.attributes(): del attr # get rid of attrs other than weight
  ecount = base_graph.ecount() # This is where edge attributes for appended graphs should start
  base_graph.es["weight0"] = base_graph.es["weight"]
  base_graph["time_idx"] = "0: %s" % os.path.splitext(os.path.basename(graphs[0]))[0]
  base_graph["num_edges"] = "0: %d" % base_graph.ecount() # Keep track of all the graphs in a 
  del base_graph.es["weight"] # get rid of old attr

  for time_slot, graph_fn in enumerate(graphs[1:]): # Note start index
    g = igraph_io.read_arbitrary(graph_fn, informat="graphml")
    
    base_graph += g.get_edgelist() # Add new edges to current graph at eid old_ecount:new_ecount
    new_edges = [None]*ecount # Mask out all old edges
    ecount = base_graph.ecount() # Update edge count
    new_edges.extend(g.es["weight"]) # Assemble new edge weights for eids base.old_ecount:base.new_ecount
    base_graph.es["weight%d" % (time_slot+1)] = new_edges
    base_graph["time_idx"] += ", %d: %s" % \
            (time_slot+1, os.path.splitext(os.path.basename(graphs[time_slot+1]))[0])
    base_graph["num_edges"] += ", %d: %d" % (time_slot+1, g.ecount())

  return base_graph

def make_mm_tensor_graphs(graphs, output):
  """
  Serial writer for Weighted market martrix tensors to a single file.

  Format:
  Note that '# ' - is a comment
  
  Example:
  # 0:file_name0 
  # 1:file_name1
  :
  :
  # N:file_nameN

  source,target,graph#,weight
  
  First there is a mapping from graph# 's (described below) to graph file names.

  @param graphs: A list of fully qualified file names for graphs.
  @param output: The name of the tensor graph output.
  """

  f = open(output, "wb")
  for idx, g_fn in enumerate(graphs):
    f.write("# %d:%s\n" % (idx, os.path.splitext(os.path.basename(g_fn))[0]))

  f.write("\n")

  for idx, g_fn in enumerate(graphs): # Note start index
    g = igraph_io.read_arbitrary(g_fn, informat="graphml")
    for edge in g.es:
      f.write("%d,%d,%d,%d\n" % (edge.source, edge.target, idx, edge["weight"]))

    # Consider skipping a line here
  f.close()
  print "Mission complete"

def main():
  parser = argparse.ArgumentParser(description="Take any number of (potentially zipped) graphml \
      graphs and create a single tensor graph")
  parser.add_argument("output", action="store", help="The output filename of the tensor graph")
  parser.add_argument("-f", "--files", nargs="+", action="store", help="Graph files that \
      should be tensor-fied")
  parser.add_argument("-o", "--out_format", default = "mm", action="store", help="The output format. Either: \
      ['graphml', 'mm']. Default is 'mm'")
  result = parser.parse_args()

  assert result.files, "You must provide some files as input. Use -f flag"

  if result.out_format == "graphml":
    g = make_graphml_tensor_graph(result.files)
    g.write(result.output, format="graphml") # Other formats are pointless with tensors
  elif result.out_format == "mm":
    make_mm_tensor_graphs(result.files, result.output)
  else:
    sys.stderr.write("[ERROR]: Invalid format '%s'\n" % result.out_format)
  
if __name__ == "__main__":
  main()
