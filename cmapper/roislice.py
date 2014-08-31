
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
import numpy as np

import matplotlib.pyplot
import sys

import roi

#
#  roislice
#
#  Draw an ROI XY slice using matplotlib.pyplot as a pcolor graph
#

def main ():

  parser = argparse.ArgumentParser(description='Draw the ROI map of a brain.')
  parser.add_argument('niigz_file', action="store")
  parser.add_argument('--dimensions', action="store", default="xy", help="xy, xz, or yz")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  rois = roi.ROINifti ( result.niigz_file )

  data = rois.data

  # cut out the specified slice
  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimension or leave blank for xy default"

  matplotlib.pyplot.show()


if __name__ == "__main__":
  main()