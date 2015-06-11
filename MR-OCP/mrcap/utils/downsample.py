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
import downsample_atlas
import nibabel as nib
import zipfile
sys.path += [os.path.abspath("../")]
from zindex import MortonXYZ
import numpy as np
import cPickle as pickle

DEBUG = False
def downsample(g, factor=-1, ds_atlas=None, ignore_zero=True):
  """
	Downsample a graph by a scale factor.

	Downsamples by collapsing regions using an dynamically generated downsampled atlas. Rebuilding the graph takes on the order of a few minutes on a standard desktop computer with more than 4GB of RAM.
	
	**Positional Arguments**

			g: [.graphml; XML file]
					- A full sized big graph.
			factor: [int] (default = 1)
					- The downsampling factor.
			ds_atlas: [.nii; nifti image] (default = MNI152)
					- A prebuilt downsampled nifti atlas with which to downsample.
			ignore_zero: [boolean] (default = True)
					- We assume the zeroth label is outside the brain.
	
	**Returns**
	
			new graph: [.graphml; XML file]
					- The input graph downsampled to the scale of the input atlas.
  """

  start = time()
  edge_dict = defaultdict(int) # key=(v1, v2), value=weight

  if factor >= 0:
    print "Generating downsampled atlas ..." # TODO: Cythonize
    ds_atlas = downsample_atlas.create(start=factor) # Create ds atlas and an atlas map for the original atlas
  
  ds_atlas = ds_atlas.get_data() # don't care about other atlas data

  spatial_map = [0]*(int(ds_atlas.max())+1) 
  # This takes O(m)
  for e in g.es:
    src_spatial_id = long(g.vs[e.source]["spatial_id"])
    tgt_spatial_id = long(g.vs[e.target]["spatial_id"])

    src_x, src_y, src_z = MortonXYZ(src_spatial_id)
    tgt_x, tgt_y, tgt_z = MortonXYZ(tgt_spatial_id)

    src = ds_atlas[src_x, src_y, src_z]
    tgt = ds_atlas[tgt_x, tgt_y, tgt_z]

    # FIXME GK: We will skip all region zeros for all atlases which is not really true!
    if ignore_zero:
      if (src and tgt) and (src != tgt):
        if not spatial_map[src]: spatial_map[src] = `src_spatial_id` 
        if not spatial_map[tgt]: spatial_map[tgt] = `tgt_spatial_id` 

        edge_dict[(src, tgt)] += e["weight"]
    else:
      print "Never should get here"
      if not spatial_map[src]: spatial_map[src] = `src_spatial_id`
      if not spatial_map[tgt]: spatial_map[tgt] = `tgt_spatial_id` 

      edge_dict[(src, tgt)] += e["weight"]

  #import pdb; pdb.set_trace()
  del g # free me
  new_graph = igraph.Graph(n=len(spatial_map), directed=False) # len spatial_map is the # of vertices
  new_graph.vs["spatial_id"] = spatial_map
  
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
  parser.add_argument("outfn", action="store", help="Output file name")
  parser.add_argument("--informat", "-i", action="store", default="graphml", help="Input format of the graph")
  parser.add_argument("--outformat", "-o", action="store", default="graphml", help="Output format of the graph")

  result = parser.parse_args()

  if result.factor >= 0:
    g = igraph_io.read_arbitrary(result.infn, informat=result.informat)
    new_graph = downsample(g, factor=result.factor)
  elif result.ds_atlas:
    g = igraph_io.read_arbitrary(result.infn, informat=result.informat)
    new_graph = downsample(g, ds_atlas=nib.load(result.ds_atlas))
  else:
    sys.stderr.write("[ERROR]: either -f or -a flag must be specified\n")
    exit(-1)

  new_graph.write(result.outfn, format=result.outformat)

if __name__ == "__main__":
  main()
