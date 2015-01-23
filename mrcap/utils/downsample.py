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
import os
import igraph
from mrcap.atlas import Atlas 
from mrcap.utils import igraph_io
from time import time
import create_atlas
import nibabel as nib
import zipfile

def downsample(g, factor=0, atlas=None):
  """
  Downsample a graph by collapsing regions using an dynamically
  generated downsampled atlas. Rebuilding the graph takes O(m).

  @param g: A full sized **big graph**
  @param factor: The downsampling factor
  @param atlas: A prebuilt nifti atlas with which to downsample
  """

  start = time()
  edge_dict = defaultdict(int) # key=(v1, v2), value=weight

  if factor:
    print "Generating atlas ..." # TODO: Cythonize
    atlas = Atlas(create_atlas.create(start=factor)) # Dynamically create atlas
  else:
    atlas = Atlas(atlas)
  
  vertex = {}
  # This takes O(m)
  for e in g.es:
    edge_dict[(atlas.get_region_num(e.source), atlas.get_region_num(e.target))] += e["weight"]

  del g # free me
  new_graph = igraph.Graph(n=atlas.max(), directed=False)
  print "Adding edges to graph ..."
  new_graph += edge_dict.keys()

  print "Adding edge weight to graph ..."
  new_graph.es["weight"] = edge_dict.values()

  print "Completed building graph in %.3f sec ... " % (time() - start)
  print new_graph.summary()
  return new_graph

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("infn", action="store", help="Input file name")
  parser.add_argument("-f", "--factor", action="store", type=int, help="Downsampling factor")
  parser.add_argument("-a", "--atlas", action="store", help="Downsampling atlas file name")
  parser.add_argument("outfn", action="store", help="Output file name")
  parser.add_argument("--informat", "-i", action="store", default="graphml", help="Input format of the graph")
  parser.add_argument("--outformat", "-o", action="store", default="graphml", help="Output format of the graph")

  result = parser.parse_args()
  
  g = igraph_io.read_arbitrary(result.infn, informat=result.informat)

  if result.factor:
    new_graph = downsample(g, factor=result.factor)
  elif result.atlas:
    new_graph = downsample(g, atlas=nib.load(result.atlas))
  else:
    sys.stderr.write("[ERROR]: either -f or -a flag must be specified\n")
    exit(-1)

  new_graph.write(result.outfn, format=result.outformat)

if __name__ == "__main__":
  main()
