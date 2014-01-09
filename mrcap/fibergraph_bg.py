# Class holding big fibergraphs
# @author Randal Burns, Disa Mhembere

from mrcap.fiber import Fiber
import mrcap.roi as roi
#import mrcap.mask as mask
import zindex
import math
import itertools
import igraph
from collections import defaultdict
from fibergraph import _FiberGraph
from time import time

# Class functions documented in fibergraph.py

class FiberGraph(_FiberGraph):
  def __init__(self, matrixdim, rois, mask):

    # Regions of interest
    self.rois = rois
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight

    # Brainmask
#    self.mask = mask

    # Round up to the nearest power of 2
    xdim = int(math.pow(2,math.ceil(math.log(matrixdim[0],2))))
    ydim = int(math.pow(2,math.ceil(math.log(matrixdim[1],2))))
    zdim = int(math.pow(2,math.ceil(math.log(matrixdim[2],2))))

    # Need the dimensions to be the same shape for zindex
    xdim = ydim = zdim = max(xdim, ydim, zdim)

    # largest value is -1 in each dimension, then plus one because range(10) is 0..9
    self._maxval = zindex.XYZMorton([xdim-1,ydim-1,zdim-1]) + 1

    # ======================================================================== #
    self.spcscmat = igraph.Graph(n=self._maxval, directed=False) # make new igraph with adjacency matrix to be (maxval X maxval)
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight
    # ======================================================================== #

  #
  # Destructor
  #
  def __del__(self):
    pass

  def add (self, fiber):
    """
    Add edges associated with a single fiber of the graph

    positonal args:
    ==============
    fiber: the fiber whose edges you want to add
    """

    # Get the set of voxels in the fiber
    allvoxels = fiber.getVoxels()

    # Voxels for the big graph
    voxels = []

    for i in allvoxels:
      xyz = zindex.MortonXYZ(i)

      # Use only the important voxels
      roival = self.rois.get(xyz)
      # if it's an roi and in the brain
      if roival:
        voxels.append(i)

    voxel_edges = itertools.combinations((voxels), 2)

    for list_item in voxel_edges:
      self.edge_dict[tuple(sorted(list_item))] += 1
