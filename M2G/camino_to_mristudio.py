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

    # GK FIXME: Need to add headers
    self.fhandle.seek(128)

  def write_path(self, path):
    """
    Write the path to disk
    
    @param path we want to write
    """

    fmt = "<ic"+"c"*3+"ii"
    _bin = struct.pack(fmt, len(path), chr(0), chr(255), chr(0), chr(0), 0, (len(path)-1))
    self.fhandle.write(_bin)
    
    # GK FIXME: Figure out how to not loop too many I/O accesses
    for voxel in path:
      _bin = struct.pack("f"*len(voxel), *voxel)
      self.fhandle.write(_bin)

  def __del__ (self,):
    self.fhandle.close()
