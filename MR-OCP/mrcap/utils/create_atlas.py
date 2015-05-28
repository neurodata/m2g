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

# create_atlas.py
# Created by Disa Mhembere on 2014-04-10.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# This simply takes a (182, 218, 182) atlas and creates
# a ~30-non-zero k region atlas by relabelling each
#   3x3x3 region with a new label then masking
# using a base atlas

import argparse
import nibabel as nib
import numpy as np
from math import ceil
from copy import copy
import sys, pdb
from time import time
import os
from packages.utils.setup import get_files

def create(roifn=os.path.join(os.environ["M2G_HOME"],"data","Atlas", 
          "MNI152_T1_1mm_brain.nii"), start=2):
  """
	Creates an Atlas from a template brain.

  Create a new atlas given some scaling factor determined by the start index. Can be useful if looking for parcellation of certain scale for graph generation.

	**Positional Arguments**
	
  		roifn: [nifti] (default = MNI152)
					- nifti roi mask file name
			start: [int] (default = 2)
					- the x,y,z start position which determines the scaling. 
  """

  start_time = time()
  atlmap = None
  print "Loading rois as base ..."
  if not os.path.exists(roifn):
    get_files()
  img = nib.load(roifn)
  base = img.get_data()
  aff = img.get_affine()
  fm = img.file_map
  true_dim = base.shape

  # Labelling new 
  label_used = False
  print "Labeling new ..."
  region_num = 1

  step = 1+(start*2)
  mstart = -start
  mend = start+1

  # Align new to scale factor
  xdim, ydim, zdim = map(ceil, np.array(base.shape)/float(step)) 
  if step == 1:
    assert xdim == base.shape[0] and ydim == base.shape[1] and zdim == base.shape[2]
  resized_base = np.zeros((xdim*step, ydim*step, zdim*step), dtype=int)
  resized_base[:base.shape[0], :base.shape[1], :base.shape[2]] = base
  base = resized_base
  del resized_base

  # Create new matrix
  new = np.zeros_like(base, dtype=np.int) # poke my finger in the eye of bjarne

  # TODO: Cythonize
  for z in xrange(start, base.shape[2]-start, step):
    for y in xrange(start, base.shape[1]-start, step):
      for x in xrange(start, base.shape[0]-start, step):

        if label_used: 
          region_num += 1 # only increase counter when a label was used
          label_used = False

        # set other (step*step)-1 around me to same region
        for zz in xrange(mstart,mend):
          for yy in xrange(mstart,mend):
            for xx in xrange(mstart,mend):
              if (base[x+xx,y+yy,z+zz]): # Masking
                label_used = True
                new[x+xx,y+yy,z+zz] = region_num
  
  new = new[:true_dim[0], :true_dim[1], :true_dim[2]] # shrink new to correct size
  print "Your atlas has %d regions ..." % len(np.unique(new))

  img = nib.Nifti1Image(new, affine=img.get_affine(), header=img.get_header(), file_map=img.file_map)
  
  del new
  print "Building atlas took %.3f sec ..." % (time()-start_time)

  return img

def validate(atlas_fn, roifn):
  """
  Validate that an atlas you've created is a valid based on the
  masking you have

  @param atlas_fn: the new atlas you've created
  @param roifn: nifti roi file name
  """

  base = nib.load(roifn).get_data()
  try:
    new = nib.load(atlas_fn).get_data()
  except:
    sys.stderr.write("[Error]: Loading file %s failed!\n" % atlas_fn);
    exit(-1)

  # This is a mapping from base to new where if we get any conflicting regions we failed to make a valid atlas
  old_to_new = {}

  for i in xrange(new.shape[2]):
    for ii in xrange(new.shape[1]):
      for iii in xrange(new.shape[0]):
        if old_to_new.has_key(base[i,ii,iii]):
          if old_to_new[base[i,ii,iii]] != new[i,ii,iii]:
            print "[Error]; Index [%d,%d,%d] Should be: {0}, but is {1}".format(i, ii, iii, 
                  old_to_new[base[i,ii,iii]], new[i,ii,iii])
            exit(911)
        else:
          if start == 0 and new[i,i,iii] in old_to_new.values(): import pdb; pdb.set_trace()
          old_to_new[base[i,ii,iii]] = new[i,i,iii]

  print "Success! Validation complete."

def main():
  parser = argparse.ArgumentParser(description="Create a downsampled atlas for a fibergraph")
  parser.add_argument("baseatlas", action="store", help="NIFTI roi")
  parser.add_argument("-n","--niftifn",  action="store", default="atlas.nii", \
          help="Nifti output file name if creating else the input file name if validation")
  parser.add_argument("-f", "--factor", default=2, action="store", type=int, \
      help="Downsample factor/Start index")
  parser.add_argument("-v", "--validate", action="store_true", help="Perform validation")

  result = parser.parse_args()
  if result.validate:
    print "Validating %s..." % result.niftifn
    validate(result.niftifn, result.baseatlas)
    exit(1)
  
  img = create(result.baseatlas, result.factor)
  nib.save(img, result.niftifn)

if __name__ == "__main__":
  main()
