
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

# Class holding small fibergraphs
# @author Randal Burns, Disa Mhembere

import math
import itertools
import os
from collections import defaultdict

import igraph

from mrcap.atlas import Atlas
from mrcap.fibergraph import _FiberGraph
from mrcap.fiber import Fiber
import scipy.io as sio
import zindex

# Class functions documented in fibergraph.py

class FiberGraph(_FiberGraph):
  def __init__(self, matrixdim, rois, mask):
    """
     Constructor: number of nodes in the graph
       convert it to a maximum element
    """
    # Regions of interest
    self.rois = rois
    # Edges
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight

    # Get the maxval from the number of rois
    self._maxval = int(self.rois.data.max())+1 

    # list of list matrix for one by one insertion
    self.spcscmat = igraph.Graph(n=self._maxval, directed=False) # make new igraph with adjacency matrix to be (maxval X maxval)

  def complete(self, add_centroids=True, graph_attrs={}, atlas={}):
    super(FiberGraph, self).complete()
    
    assert atlas, "One Atlas must exist for any small graph!"
    # since only 1 atlas
    atlas_name = atlas.keys()[0]
    atlas_regions = atlas[atlas.keys()[0]]

    print "Attempting to add atlas labels ..."
    if atlas_regions is not None:
      f_regions = open(atlas_regions, "rb")
      self.spcscmat.vs["region_name"] = f_regions.read().splitlines()
    
    if add_centroids:
      print "Adding centroids ..."
      cent_mat = sio.loadmat(os.path.join(os.path.abspath(os.path.dirname(__file__)),"utils", "centroids.mat"))["centroids"]
      centroids = []

      for row in cent_mat:
        centroids.append(str(list(row)))

      self.spcscmat.vs["centroid"] = centroids
    
    for key in graph_attrs.keys():
      self.spcscmat[key] = graph_attrs[key]
