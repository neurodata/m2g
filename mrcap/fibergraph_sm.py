from scipy.sparse import lil_matrix, csc_matrix
from scipy.io import loadmat, savemat
from mrcap.fiber import Fiber
import mrcap.roi as roi
import mrcap.mask as mask
import zindex
import math
import itertools
from cStringIO import StringIO
import igraph
from time import time
"""
 fibgergraph_sm provides the same interfaces as fibergraph but
  makes the 70 x 70 matrix


  This routine uses two different sparse matrix representations.
  The calls need to be performed in the following order

    Create FiberGraph
    Add Edges (lil format)
    Complete -- this converts from dictionary of keys format to Column CSC
    Write or SVD (on csc format)

"""

class FiberGraph:
  """
    Sparse matrix representation of a Fiber graph
  """

  def __init__(self, matrixdim, rois, mask ):
    """
     Constructor: number of nodes in the graph
       convert it to a maximum element
    """

    # Regions of interest
    self.rois = rois
    self.sorted_edges = [] # Will hold all edges to be added to the graph in self.complete

    # Brainmask
#    self.mask = mask

    # Get the maxval from the number of rois
#    self._maxval = rois.maxval()
    self._maxval = 70

    # ======================================================================== #
    # list of list matrix for one by one insertion
    #**self.spedgemat = lil_matrix ( (self._maxval, self._maxval), dtype=float )
    self.spcscmat = igraph.Graph(directed=True) # make new igraph graph
    self.spcscmat += self._maxval # shape the adjacency matrix to be (maxval X maxval)
    # ======================================================================== #

    # empty CSC matrix
    #self.spcscmat = csc_matrix ( (self._maxval, self._maxval), dtype=float )

  def __del__(self):
    """
      Destructor
    """
    pass

  #
  # Add a fiber to the graph.
  #  This is not idempotent, i.e. if you add the same fiber twice you get a different result
  #  in terms of graph weigths.
  #
#  def add ( self, fiber ):
#    """Add a fiber to the graph"""
#
#    # Get the set of voxels in the fiber
#    allvoxels = fiber.getVoxels ()
#
#    roilist = []
#    # Use only the important voxels
#    for i in allvoxels:
#
#    # this is for the small graph version
#       xyz = zindex.MortonXYZ(i)
#       roival = self.rois.get(xyz)
#       # if it's an roi and in the brain
##       if roival and self.mask.get (xyz):
#       if roival:
#         roilist.append ( roi.translate( roival ) )
#
#    roilist = set ( roilist )
#
#    roi_edges = itertools.combinations((roilist),2)
#
#    roi_edges_sorted = []
#    for list_item in roilist_edges:
#      roi_edges_sorted.append(tuple(sorted(list_item)))
#
#    for v1,v2 in itertools.combinations((roilist),2):
#
#      if ( v1 < v2 ):
#        #** self.spedgemat [ v1, v2 ] += 1.0
#        self.spedgemat += (v1, v2)
#      else:
#        self.spedgemat += (v2, v1)
#        #** self.spedgemat [ v2, v1 ] += 1.0

  def add ( self, fiber ):
    """
    Add edges associated with a single fiber of the graph

    positonal args:
    ==============
    fiber: the fiber whose edges you want to add
    """

    # Get the set of voxels in the fiber
    allvoxels = fiber.getVoxels ()

    roilist = []
    # Use only the important voxels
    for i in allvoxels:

    # this is for the small graph version
       xyz = zindex.MortonXYZ(i)
       roival = self.rois.get(xyz)
       # if it's an roi and in the brain
       if roival:
         roilist.append ( roi.translate( roival ) )

    roilist = set ( roilist )

    roi_edges = itertools.combinations((roilist),2)

    for list_item in roi_edges:
      self.sorted_edges.append(tuple(sorted(list_item)))

  #
  # Complete the graph.  Get it ready for analysis.
  #
  def complete ( self ):
    """Done adding fibers.  Prior to analysis"""
    start = time()
    print "Adding all edges to the graph ..."
    self.spcscmat += self.sorted_edges
    print "Completed adding edges in %.3f sec" % ( time () - start)


    #**self.spcscmat = csc_matrix ( self.spedgemat )
    #**del self.spedgemat

  #
  #  Write the sparse matrix out in a format that can be reingested.
  #  fout should be an open file handle
  #
  def saveToMatlab ( self, key, filename ):
    """Save the sparse array to disk in the specified file name"""

    if 0 == self.spcscmat.getnnz():
      print "Call complete after adding all edges"
      assert 0

    print "Saving key ", key, " to file ", filename
    savemat( filename , {key: self.spcscmat})

  #
  #  Write the sparse matrix out in a format that can be reingested.
  #  fout should be an open file handle
  #
  def loadFromMatlab ( self, key, filename ):
    """Load the sparse array from disk by file name"""

    print "Reading key ", key, " from file ", filename

    # first convert to csc
    t = loadmat ( filename  )
    self.spcscmat = t[key]

  # ========================================================================== #
  def saveToIgraph( self, filename, format="picklez" ):
    """ Save igraph sparse matrix """
    self.spcscmat.save( filename, format=format )

  def loadFromIgraph( self, filename, format="picklez" ):
    """ Load a sparse matrix from igraph as a numpy pickle """
    igraph.load( filename, format=format )

  # ========================================================================== #