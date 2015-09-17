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
    
    # Keep track of the original vertex ID = region ID before deletion deg zero vertices
    print "Annotating vertices with spatial position for big graph.."
    spatial_map = [`0`]*(self.graph.vcount()+1)
    nnz = np.where(self.rois.data != 0)
    for idx in xrange(nnz[0].shape[0]):
      x,y,z = nnz[0][idx], nnz[1][idx], nnz[2][idx]
      region_id = self.rois.data[x,y,z]
      spatial_map[region_id] = `XYZMorton([x,y,z])` # Use to get the spatial position of a vertex

    self.graph.vs["spatial_id"] = spatial_map
    
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight
    # ======================================================================== #

  def complete(self, add_centroids=True, graph_attrs={}, atlases={}):
    super(FiberGraph, self).complete()
    centroids_added = False

    for idx, atlas_name in enumerate(atlases.keys()):
      self.graph["Atlas_"+ os.path.splitext(os.path.basename(atlas_name))[0]+"_index"] = idx

    for key in graph_attrs.keys():
      self.graph[key] = graph_attrs[key]
