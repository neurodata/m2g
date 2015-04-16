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

import math
import os
from collections import defaultdict

import numpy as np
import igraph
import scipy.io as sio

from mrcap.fiber import Fiber
import mrcap.roi as roi
from mrcap.fibergraph import _FiberGraph
from mrcap.atlas import Atlas
from zindex import XYZMorton
from packages.utils.setup import get_files

# Class functions documented in fibergraph.py

class FiberGraph(_FiberGraph):
  def __init__(self, matrixdim, rois, atlases={}):

    # Regions of interest
    self.rois = rois
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight

    # Round up to the nearest power of 2
    xdim = int(math.pow(2,math.ceil(math.log(matrixdim[0],2))))
    ydim = int(math.pow(2,math.ceil(math.log(matrixdim[1],2))))
    zdim = int(math.pow(2,math.ceil(math.log(matrixdim[2],2))))

    # Need the dimensions to be the same shape for zindex
    xdim = ydim = zdim = max(xdim, ydim, zdim)
    # largest value is -1 in each dimension, then plus one because range(10) is 0..9

    position = [] # This is the original (true) vertex/voxel id before vertex deletion
    # FIXME DM: Assumption is voxels are row-ordered -- confirm with GK.
    for x in xrange(matrixdim[0]):
      for y in xrange(matrixdim[1]):
        for z in xrange(matrixdim[2]):
          position.append(XYZMorton([x,y,z]))

    self._maxval = XYZMorton([xdim-1,ydim-1,zdim-1]) + 1

    # ======================================================================== #
    # make new igraph with adjacency matrix to be (maxval X maxval)
    self.spcscmat = igraph.Graph(n=self._maxval, directed=False)
    # The original vertex ID is maintained using the  position field
    self.spcscmat.vs["position"] = position
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight
    # ======================================================================== #

  def complete(self, add_centroids=True, graph_attrs={}, atlases={}):
    super(FiberGraph, self).complete()
    print "Annotating vertices with spatial position .."
    centroids_added = False

    print "Deleting zero-degree nodes..."
    zero_deg_nodes = np.where( np.array(self.spcscmat.degree()) == 0 )[0]
    self.spcscmat.delete_vertices(zero_deg_nodes)
    
    for idx, atlas_name in enumerate(atlases.keys()):
      self.spcscmat["Atlas_"+ os.path.splitext(os.path.basename(atlas_name))[0]+"_index"] = idx
      print "Adding '%s' region numbers (and names) ..." % atlas_name
      atlas = Atlas(atlas_name, atlases[atlas_name])
      #region = atlas.get_all_mappings(self.spcscmat.vs["position"])
      #self.spcscmat.vs["atlas_%d_region_num" % idx] = region[0]
      #if region[1]: self.spcscmat.vs["atlas_%d_region_name" % idx] = region[1]
    
      if add_centroids and (not centroids_added):
        if (atlas.data.max() == 70): #FIXME: Hard coded Desikan small dimensions
          centroids_added = True
          print "Adding centroids ..."
          cent_loc = os.path.join("../../", "data", "Centroids", "centroids.mat")
          if not os.path.exists(cent_loc):
            get_files()

          cent_mat = sio.loadmat(cent_loc)["centroids"]

          keys = atlas.get_region_nums(self.spcscmat.vs["position"])
          centroids = []
          for key in keys:
            centroids.append(str(list(cent_mat[key-1]))) # -1 accounts for 1-based indexing

          self.spcscmat.vs["centroid"] = centroids

    for key in graph_attrs.keys():
      self.spcscmat[key] = graph_attrs[key]
