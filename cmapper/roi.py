
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

import sys
import os
import numpy as np
import nibabel as nib

#
#  Load a NIFTi file and create an ROImap
#

class ROINifti:
  """Class to read ROI data derived from NIFTi files.""" 

  def __init__(self, filename):

    self._img = nib.load(filename)

    print "Shape %s, type %s img.shape" % ( self._img.shape, self._img.get_data_dtype() )

    self.data = self._img.get_data()

    print self.data.shape

  def get ( self, index ):
    """Returns the ROI associated with a voxel.
      Either returns 0 if out of the data space or 
      returns ROI value
    """

    if index[0] >= self.data.shape[0] or \
       index[1] >= self.data.shape[1] or \
       index[2] >= self.data.shape[2]: 
      return 0
    else:
      return self.data [ index[0], index[1], index[2] ]
