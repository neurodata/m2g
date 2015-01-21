#!/usr/bin/python

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

# camino_to_mristudio.py
# Created by Disa Mhembere on 2015-01-13.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import struct

class MRIstudio(object):
  """
  This class represents an MRI studio format file.
  It write out data in the format given a path which is
  a list of 3-tuples.

  """
  def __init__(self, filename):
    """
    @param filename: the output fn
    """
    self.fhandle = open(filename, "wb")


    # ('sFiberFileTag','a8'), ('nFiberNr','i4'), ('nFiberLenMax','i4'), 
    # ('fFiberLenMean','f4'), ('nImgWidth','i4'), ('nImgHeight','i4'), 
    # ('nImgSlices', 'i4'), ('fPixelSizeWidth','f4'), 
    # ('fPixelSizeHeight','f4'), ('fSliceThickness','f4'),
    # ('enumSliceOrientation','i1'), ('enumSliceSequencing','i1'), ('sVersion','a8')

    # GK FIXME: Need to add real headers
    self.fhandle.write(struct.pack("c"*8, *"FiberDat"))

    file_header_fmt = "iifiiifffcc"+"c"*8
    self.fhandle.write(struct.pack(file_header_fmt,-1,-1, -1.0, -1, -1, -1, 
      -1.0, -1.0, -1.0, chr(0), chr(0), *"        "))
    

    self.fiber_header_fmt = "<ic"+"c"*3+"ii" # Each fiber starts with thi
    self._rewind()

  def set_num_fibers(self, count):
    """
    Set the number of fibers within the file so that the
    graph generation script does throw a hissy

    @param count: The number of fibers in the 
    """
    self.fhandle.seek(8)
    self.fhandle.write(struct.pack("i", count))

  # Thank RB for this nomecleture. Who knows ...?
  def _rewind(self, ):
    self.fhandle.seek(128)

  def write_path(self, path):
    """
    Write the path to disk
    
    @param path we want to write
    """

    _bin = struct.pack(self.fiber_header_fmt, len(path), chr(0), 
        chr(255), chr(0), chr(0), 0, (len(path)-1))
    self.fhandle.write(_bin)
    
    # GK FIXME: Figure out how to not loop too many I/O accesses
    for voxel in path:
      _bin = struct.pack("f"*len(voxel), *voxel)
      self.fhandle.write(_bin)

  def __del__ (self,):
    self.fhandle.close()
