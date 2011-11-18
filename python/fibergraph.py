##############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

from scipy.sparse import dok_matrix 
from fiber import Fiber
import zindex

#
#  Sparse matrix representation of a Fiber graph
#
class FiberGraph:

  #
  # Constructor: number of nodes in the graph
  #   convert it to a maximum element
  #
  def __init__(self, matrixdim ):
    self._maxval = zindex.XYZMorton ( matrixdim )
    self.spedgemat = dok_matrix ( (self._maxval, self._maxval), dtype=float )

  #
  # Destructor
  #
  def __del__(self):
    self.spedgemat.clear()

  #
  # Add a fiber to the graph.  
  #  This is not idempotent, i.e. if you add the same fiber twice you get a different result
  #  in terms of graph weigths.
  #
  def add ( self, fiber ):
    edgelist = fiber.getEdges ()
    for edge in edgelist: 
      self.spedgemat [ edge[0], edge[1] ] += 1.0

# RBTEST
  def check ( self ):

    for k,v in self.spedgemat.iteritems():
      print zindex.MortonXYZ ( k[0] ), zindex.MortonXYZ ( k[1] ), v


      
