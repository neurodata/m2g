#!/usr/bin/python

# atlas.py
# Created by Disa Mhembere on 2014-01-08.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

from zindex import MortonXYZ
import scipy.io as sio
import nibabel as nib
import os

class Atlas(object):
  def __init__(self, atlas_fn, label_fn=None):
    self.data = nib.load(os.path.abspath(atlas_fn)).get_data()
    if label_fn: 
      label_file = open(label_fn, "rb")
      self.region_names = label_file.read().splitlines()
    else:
      self.region_names = None

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
      keys.append(self.get_region_num(vertex))
    return keys 
