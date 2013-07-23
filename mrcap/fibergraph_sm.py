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
    self.spcscmat = igraph.Graph(n=self._maxval, directed=True) # make new igraph with adjacency matrix to be (maxval X maxval)
    # ======================================================================== #

    # empty CSC matrix
    #self.spcscmat = csc_matrix ( (self._maxval, self._maxval), dtype=float )

  def __del__(self):
    """
      Destructor
    """
    pass

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
    print "Adding %d edges to the graph ..." % len(self.sorted_edges)
    self.spcscmat += self.sorted_edges
    print "Completed adding edges in %.3f sec" % ( time () - start)


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