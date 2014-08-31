
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
import mask
import sys

#
#  maskslice
#
#  Draw a brain mask slice using matplotlib.pyplot as a pcolor graph
#

#
# main
#
def main ():

  parser = argparse.ArgumentParser(description='Draw the mask map of a brain.')
  parser.add_argument('maskxmlfile', action="store")
  parser.add_argument('maskrawfile', action="store")
  # RBTODO how to make 0,1,2 the legal values
  parser.add_argument('--dimensions', action="store", default="xy")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  try:
    maskx = mask.MaskXML( result.maskxmlfile )
    masks = mask.MaskData ( result.maskrawfile, maskx.getShape() ) 
  except:
    # RBTODO give a meaningful error 
    print "Failed to parse brain mask files at: ", result.maskxmlfile, result.maskxmlfile
    sys.exit ( -1 ) 

  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( masks.data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( masks.data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( masks.data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimensino or leave blank for xy default"


  raw_input("Press Enter to continue...")

if __name__ == "__main__":
  main()