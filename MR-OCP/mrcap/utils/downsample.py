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

# downsample.py
# Created by Disa Mhembere on 2014-07-08.
# Email: disa@jhu.edu

import argparse
from glob import glob
from collections import defaultdict
import os, sys
import igraph
from mrcap.atlas import Atlas 
from mrcap.utils import igraph_io
from time import time
import create_atlas
import nibabel as nib
import zipfile
sys.path += [os.path.abspath("../")]
from zindex import MortonXYZ
import numpy as np
import cPickle as pickle

DEBUG = False
def downsample(g, factor=-1, ds_atlas=None, orig_atlmap=None):
  """
  Downsample a graph by collapsing regions using an dynamically
  generated downsampled atlas. Rebuilding the graph takes O(m).

  @param g: A full sized **big graph**
  @param factor: The downsampling factor
  @param ds_atlas: A prebuilt downsampled nifti atlas with which to downsample
  """

  start = time()
  edge_dict = defaultdict(int) # key=(v1, v2), value=weight

  if factor >= 0:
    print "Generating downsampled atlas ..." # TODO: Cythonize
    ds_atlas, orig_atlmap = create_atlas.create(start=factor) # Create ds atlas and an atlas map for the original atlas
  
  ds_atlas = ds_atlas.get_data() # don't care about other atlas data

  # This takes O(m)
  for e in g.es:
    #import pdb; pdb.set_trace()
    src = ds_atlas[orig_atlmap[ (g.vs[e.source]["position"]) ]]
    tgt = ds_atlas[orig_atlmap[ (g.vs[e.target]["position"]) ]]

    edge_dict[(src, tgt)] += e["weight"]

  del g # free me
  new_graph = igraph.Graph(n=ds_atlas.max().take(0), directed=False)
  print "Adding edges to graph ..."
  new_graph += edge_dict.keys()

  print "Adding edge weight to graph ..."
  new_graph.es["weight"] = edge_dict.values()

  print "Deleting zero-degree nodes..."
  zero_deg_nodes = np.where(np.array(new_graph.degree()) == 0 )[0]
  new_graph.delete_vertices(zero_deg_nodes)

  print "Completed building graph in %.3f sec ... " % (time() - start)
  print new_graph.summary()
  return new_graph

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("infn", action="store", help="Input file name")
  parser.add_argument("-f", "--factor", action="store", type=int, help="Downsampling factor")
  parser.add_argument("-a", "--ds_atlas", action="store", help="Pre-Downsampled atlas file name")
  parser.add_argument("-m", "--atlas_map", action="store", help="Downsampling atlas map file name")
  parser.add_argument("outfn", action="store", help="Output file name")
  parser.add_argument("--informat", "-i", action="store", default="graphml", help="Input format of the graph")
  parser.add_argument("--outformat", "-o", action="store", default="graphml", help="Output format of the graph")

  result = parser.parse_args()

  if result.factor >= 0:
    g = igraph_io.read_arbitrary(result.infn, informat=result.informat)
    new_graph = downsample(g, factor=result.factor)
  elif result.ds_atlas:
    with open(result.atlas_map, "rb") as f:
      orig_atlmap = pickle.load(f)

    g = igraph_io.read_arbitrary(result.infn, informat=result.informat)
    new_graph = downsample(g, ds_atlas=nib.load(result.ds_atlas), orig_atlmap=orig_atlmap)
  else:
    sys.stderr.write("[ERROR]: either -f or -a flag must be specified\n")
    exit(-1)

  new_graph.write(result.outfn, format=result.outformat)

if __name__ == "__main__":
  main()
