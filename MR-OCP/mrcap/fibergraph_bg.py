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

# Class holding big fibergraphs
# @author Randal Burns, Disa Mhembere

import os
from collections import defaultdict

import igraph
import scipy.io as sio
import numpy as np

from mrcap.fiber import Fiber
import mrcap.roi as roi
from mrcap.fibergraph import _FiberGraph
from mrcap.atlas import Atlas
from zindex import XYZMorton
from packages.utils.setup import get_files

# Class functions documented in fibergraph.py

class FiberGraph(_FiberGraph):
  def __init__(self, matrixdim, rois, atlases={}):
    super(FiberGraph, self).__init__(matrixdim, rois)

    """
    # Regions of interest
    self.rois = rois
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight

    # ======================================================================== #
    # make new igraph with adjacency matrix to be (maxval X maxval)
    self.graph = igraph.Graph(n=self.rois.data.max().take(0), directed=False)
    """
    
    # Keep track of the original vertex ID = region ID before deletion deg zero vertices
    print "Annotating vertices with spatial position .."
    spatial_map = [0]*(self.graph.vcount()+1)
    nnz = np.where(self.rois.data != 0)
    for idx in xrange(nnz[0].shape[0]):
      x,y,z = nnz[0][idx], nnz[1][idx], nnz[2][idx]
      region_id = self.rois.data[x,y,z]
      spatial_map[region_id] = XYZMorton([x,y,z]) # Use to get the spatial position of a vertex

    self.graph.vs["spatial_id"] = spatial_map
    
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight
    # ======================================================================== #

  def complete(self, add_centroids=True, graph_attrs={}, atlases={}):
    super(FiberGraph, self).complete()
    centroids_added = False

    """
    print "Deleting zero-degree nodes..."
    zero_deg_nodes = np.where( np.array(self.graph.degree()) == 0 )[0]
    self.graph.delete_vertices(zero_deg_nodes)
    """
    
    for idx, atlas_name in enumerate(atlases.keys()):
      self.graph["Atlas_"+ os.path.splitext(os.path.basename(atlas_name))[0]+"_index"] = idx
      print "Adding '%s' region numbers (and names) ..." % atlas_name
      atlas = Atlas(atlas_name, atlases[atlas_name])
      #region = atlas.get_all_mappings(self.graph.vs["position"])
      #self.graph.vs["atlas_%d_region_num" % idx] = region[0]
      #if region[1]: self.graph.vs["atlas_%d_region_name" % idx] = region[1]
    
      if add_centroids and (not centroids_added):
        if (atlas.data.max() == 70): #FIXME: Hard coded Desikan small dimensions
          centroids_added = True
          print "Adding centroids ..."
          cent_loc = os.path.join("../../", "data", "Centroids", "centroids.mat")
          if not os.path.exists(cent_loc):
            get_files()

          cent_mat = sio.loadmat(cent_loc)["centroids"]

          keys = atlas.get_region_nums(self.graph.vs["position"])
          centroids = []
          for key in keys:
            centroids.append(str(list(cent_mat[key-1]))) # -1 accounts for 1-based indexing

          self.graph.vs["centroid"] = centroids

    for key in graph_attrs.keys():
      self.graph[key] = graph_attrs[key]
