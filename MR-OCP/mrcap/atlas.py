#!/usr/bin/env python

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

# atlas.py
# Created by Disa Mhembere on 2014-01-08.
# Email: disa@jhu.edu

from zindex import MortonXYZ
import scipy.io as sio
import nibabel as nib
import os

class Atlas(object):
  def __init__(self, atlas, label_fn=None):
    """
    The use of this ctor is such that the `atlas` arg can either
    be a nifti image or the path to a nifti image from which
    I may obtain the nifti image and associated metadata.
    
    @param atlas: The atlas filename or nibabel nifti object
    @param label_fn: If there is a atlas region label file
    """
    if isinstance(atlas, str) or isinstance(atlas, unicode):
      self.data = nib.load(os.path.abspath(atlas)).get_data()
    else:
      self.data = atlas.get_data()

    if label_fn: 
      label_file = open(label_fn, "rb")
      self.region_names = label_file.read().splitlines()
    else:
      self.region_names = None

  def max(self):
    return self.data.max()

  def get_region_num(self, vertex):
    x,y,z = MortonXYZ(vertex)
    return (self.data[x, y, z])

  def get_region_name(self, region_num):
    assert self.region_names, "No atlas region names file specified"
    return self.region_names[int(region_num) - 1] # -1 for the 1-based indexing 

  def get_all_mappings(self, vertices):
    region_nums = []
    region_names = [] 
    for vertex in vertices:
      region_num = self.get_region_num(vertex)
      region_nums.append(region_num)
      if self.region_names: region_names.append(self.get_region_name(region_num))
    
    return region_nums, region_names

  def get_region_nums(self, vertices):
    """
    Get a bunch of region numbers given vertex index
    """
    keys = []
    for vertex in vertices:
      keys.append(self.get_region_num(int(vertex))) # TODO: Verify me
    return keys 
