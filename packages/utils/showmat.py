
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