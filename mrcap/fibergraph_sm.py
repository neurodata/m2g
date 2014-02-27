# Class holding small fibergraphs
# @author Randal Burns, Disa Mhembere

from mrcap.fiber import Fiber
import mrcap.roi as roi
import scipy.io as sio
import zindex
import math
import itertools
import igraph
from collections import defaultdict
from mrcap.fibergraph import _FiberGraph
from mrcap.desikan import des_map
import os

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
#    self._maxval = rois.maxval()
    self._maxval = 70 # FIXME: Hardcoded

    # list of list matrix for one by one insertion
    self.spcscmat = igraph.Graph(n=self._maxval, directed=False) # make new igraph with adjacency matrix to be (maxval X maxval)

  def __del__(self):
    """
      Destructor
    """
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

    roilist = []
    # Use only the important voxels
    for i in allvoxels:

    # this is for the small graph version
       xyz = zindex.MortonXYZ(i)
       roival = self.rois.get(xyz)
       # if it's an roi and in the brain
       if roival:
         roilist.append(roi.translate(roival))

    roilist = set(roilist)
    roi_edges = itertools.combinations((roilist),2)

    for list_item in roi_edges:
      self.edge_dict[tuple(sorted(list_item))] += 1


  def complete(self, ):
    super(FiberGraph, self).complete()

    print "Adding desikan labels ..."
    self.spcscmat.vs["region"] = des_map.values()
    
    print "Adding centroids ..."
    cent_mat = sio.loadmat(os.path.join(os.path.abspath(os.path.dirname(__file__)),"utils", "centroids.mat"))["centroids"]
    centroids = []

    for row in cent_mat:
      centroids.append(str(list(row)))

    self.spcscmat.vs["centroid"] = centroids
