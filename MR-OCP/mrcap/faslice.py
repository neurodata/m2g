
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
import fa
import sys
import math

import numpy as np

#
#  faslice
#
#  Draw an FS slice using matplotlib.pyplot as a pcolor graph
#

def main ():

  parser = argparse.ArgumentParser(description='Draw the FA map of a brain.')
  parser.add_argument('faxmlfile', action="store")
  parser.add_argument('farawfile', action="store")
  parser.add_argument('--dimensions', action="store", default="xy", help="xy, xz, or yz")
  parser.add_argument('--zero_threshold', action="store", type=float, default=0.2)
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  # Read the XML file and then the data
  try:
    fax = fa.FAXML( result.faxmlfile )
    fas = fa.FAData ( result.farawfile, fax.getShape() ) 
  except:
    print "Failed to parse FA files at: ", result.faxmlfile, result.faxmlfile
    assert 0


  # cut out the specified slice
  if result.dimensions == "xy":
    graphdata = fas.data[:,:,result.slice] 
  elif result.dimensions == "yz":
    graphdata = fas.data[result.slice,:,:] 
  elif result.dimensions == "xz":
    graphdata = fas.data[:,result.slice,:] 
  else:
    print "Choose xy, xz, or yz as dimension or leave blank for xy default"

  vec_func1 = np.vectorize ( lambda x: 0.0 if math.isnan(x) else x ) 
  vec_func2 = np.vectorize ( lambda x: int ( math.fabs(x) / result.zero_threshold ) )
  fgraphdata = vec_func1 ( graphdata )
  igraphdata = vec_func2 ( fgraphdata )

  matplotlib.pyplot.pcolor ( igraphdata )
  matplotlib.pyplot.show()


if __name__ == "__main__":
  main()