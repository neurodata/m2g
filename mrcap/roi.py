
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

import nibabel as nib

#  Makes a ton of assumptions about the XML data.  
#  Totally customize for MRCAP data.  Needs to be checked with 
#  anything that's not the original 109 data files on braingraph1

class ROIData:
  """Class to read ROI data derived from MRCAP.""" 

  # Get the dimension
  def __init__(self, filename):

    self._filename = filename
    self.data = nib.load(filename).get_data()
    print "Data shape: ", self.data.shape

  def get ( self, index ):
    """Returns the ROI associated with a voxel.
      Either returns 0 if out of the data space or 
      returns ROI from 1 to 35 or 101 to 135.
      Caller must translate so that the weirdness is not
      hidden inside this function.
    """

# RBTODO experiment with -1 on index
    if index[0] >= self.data.shape[0] or \
       index[1] >= self.data.shape[1] or \
       index[2] >= self.data.shape[2]: 

      print "[Debug]: Fiber at index", index , "not in roi"
      return 0
    else:
      return self.data[ index[0], index[1], index[2] ]

# DM: Still a necessary function
# Use the crazy numbering system
def translate ( index ):
  """Turn ROIs from labels into 70 values from 0 to 69.
     Return 0-34 for 1-35.
     Return 35-69 for 101-135.
  """
  assert index > 0 and ( index <= 35 or index > 100 )
  if index > 100: 
    return index - 66
  else:
    return index - 1

