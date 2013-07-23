from scipy.sparse import lil_matrix, csc_matrix
from scipy.io import loadmat, savemat
from mrcap.fiber import Fiber
import mrcap.roi as roi
import mrcap.mask as mask
import zindex
import math
import itertools
import igraph
from cStringIO import StringIO

"""
  This routine uses two different sparse matrix representations.
  The calls need to be performed in the following order

     Create FiberGraph
     Add Edges (lil format)
     Complete -- this converts from dictionary of keys format to Column CSC
     Write or SVD (on csc format)


  Sparse matrix representation of a Fiber graph
"""

class FiberGraph:

  """
  Constructor: number of nodes in the graph
    convert it to a maximum element
  """
  def __init__(self, matrixdim, rois, mask ):

    # Regions of interest
    self.rois = rois

    # Brainmask
#    self.mask = mask

    # Round up to the nearest power of 2
    xdim = int(math.pow(2,math.ceil(math.log(matrixdim[0],2))))
    ydim = int(math.pow(2,math.ceil(math.log(matrixdim[1],2))))
    zdim = int(math.pow(2,math.ceil(math.log(matrixdim[2],2))))

    # Need the dimensions to be the same shape for zindex
    xdim = ydim = zdim = max ( xdim, ydim, zdim )

    # largest value is -1 in each dimension, then plus one because range(10) is 0..9
    self._maxval = zindex.XYZMorton ([xdim-1,ydim-1,zdim-1]) + 1

    # ======================================================================== #
    self.spcscmat = igraph.Graph(n=self._maxval, directed=True) # make new igraph DIRECTED graph
    self.sorted_edges = []
    # ======================================================================== #

  #
  # Destructor
  #
  def __del__(self):
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

    # Voxels for the big graph
    voxels = []

    for i in allvoxels:
      xyz = zindex.MortonXYZ(i)

      # Use only the important voxels
      roival = self.rois.get(xyz)
      # if it's an roi and in the brain
      if roival:
        voxels.append ( i )

    voxel_edges = itertools.combinations( ( voxels ), 2 )

    for list_item in voxel_edges:
      self.sorted_edges.append(tuple(sorted(list_item)))

  #
  # Complete the graph.  Get it ready for analysis.
  #
  def complete ( self ):
    """Done adding fibers. Prior to analysis"""
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