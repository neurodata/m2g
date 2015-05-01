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

# mni_atlas_map.py
# Created by Disa Mhembere on 2015-05-01.
# Email: disa@jhu.edu

import argparse
import nibabel as nib
import cPickle as pickle
import numpy as np
from time import time
import os

DEBUG = False
def create(atlas):
  """
  Create a dict mapping from atlas region to spacial x, y, z co-ords

  @param atlas: A 3D data memmap or nibabel atlas file name
  """
  start = time()
  region_map = {}
  
  if isinstance(atlas, str) or isinstance(atlas, unicode):
    atlas = nib.load(atlas).get_data()
  nnz = np.where(atlas != 0)
  
  # TODO: Cythonize
  for idx in xrange(nnz[0].shape[0]):
    if DEBUG:
      assert region_map.has_key(atlas[nnz[0][idx], nnz[1][idx], nnz[2][idx]]),\
          "Duplicate regions in Atlas!"

    region_map[atlas[nnz[0][idx], nnz[1][idx], nnz[2][idx]]] = \
                                      (nnz[0][idx],nnz[1][idx], nnz[2][idx])
  
  print "Total mapping time = %.3f sec" % (time() - start)
  return region_map

def main():
  parser = argparse.ArgumentParser(description="Create a serialize pickle dump of an \
      atlas mapping from region to spatial position")
  parser.add_argument("atlas_fn", action="store", help="The atlas to be mapped")
  parser.add_argument("map_fn", action="store", help="The atlas mapping filename")
  result = parser.parse_args()

  region_map = create(result.atlas)

  if os.path.splitext(result.map_fn)[1] != ".cpickle": result.map_fn += ".cpickle"
  with open(result.map_fn, "wb") as f:
    pickle.dump(region_map, f)

if __name__ == "__main__":
  main()
