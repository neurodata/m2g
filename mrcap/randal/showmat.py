import argparse
import matplotlib.pyplot
import numpy as np
from scipy.io import loadmat
from scipy.sparse import csc_matrix
import scipy

def main( matfile ):
  """
    False color graph from a mat file
    Only upper-triangular
  """
  matcontents = loadmat ( matfile )

  graphcsc = matcontents[ "fibergraph" ]
  graphdata = np.array ( graphcsc.todense() )

  print graphdata [ 0:4, 0:4 ]

  matplotlib.pyplot.pcolor ( graphdata[:,:] )
  matplotlib.pyplot.show ()

def showfullmulti( matfile ):
  """
  Author: Disa Mhembere
  contact: disa@jhu.edu
    1. False color graph from a mat file
    2. Mono-coloring for binirized mat file
    Both full graphs not upper/lower triangular
  """
  matcontents = loadmat ( matfile )

  graphcsc = matcontents[ "fibergraph" ]
  graphdata = np.array ( graphcsc.todense() )
  graphdata = graphdata + graphdata.T
  print graphdata [ 0:4, 0:4 ]
  fig = matplotlib.pyplot.pcolormesh( graphdata[:,:] )
  matplotlib.pyplot.colorbar()
  matplotlib.pyplot.show ()

  bw_graphdata = scipy.sign(graphdata)
  fig2 = matplotlib.pyplot.pcolormesh( bw_graphdata[ :,: ], cmap='Greys')#, interpolation='nearest' )
  matplotlib.pyplot.colorbar()
  matplotlib.pyplot.show ()

if __name__ == '__main__':
  parser = argparse.ArgumentParser( description='False color graph from a mat file' )
  parser.add_argument( 'matfile', action="store" )
  result = parser.parse_args()

  #main( result.matfile )
  showfullmulti( result.matfile )
