#!/usr/bin/python
# create_atlas.py
# Created by Disa Mhembere on 2014-04-10.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# This simply takes a (182, 218, 182) atlas and creates
# a ~20k region atlas by relabelling each
# FIXME: 3x3x3 region with a new label then masking
# using a base atlas

import argparse
import mrcap.roi as roi
import nibabel as nib
import numpy as np
from math import ceil
from copy import copy

def create(roixmlfn, roirawfn, outfn):
  #nifti_base = nib.load(baseatlasfn)

  print "Loading rois as base ..."
  base = roi.ROIData (roirawfn, roi.ROIXML(roixmlfn).getShape()).data
  base = copy(base) # shallow
  #base = np.ones((182, 218, 182), dtype=int)
  true_dim = base.shape

  # Labelling new 
  label_used = False
  print "Labeling new ..."
  region_num = 1

  start = 3
  step = 1+(start*2)
  mstart = -start
  mend = (-mstart)+1 
  
  # Align to scale factor
  xdim, ydim, zdim = map(ceil, np.array(base.shape)/float(step)) 
  base.resize(xdim*step, ydim*step, zdim*step)

  # Create new matrix
  new = np.zeros_like(base) # poke my finger in the eye of malloc

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

  new = np.resize(new, true_dim)
  img = nib.Nifti1Image(new, nib.load("./desikan_atlas.nii").get_affine()) # FIXME: Ask
  nib.save(img, outfn)

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("roixmlfn", action="store", help="")
  parser.add_argument("roirawfn", action="store", help="")
  parser.add_argument("-o","--outfn",  action="store", default="atlas.nii", help="")
  parser.add_argument("-s", "--scale_factor", action="store", help="")
  result = parser.parse_args()

  create(result.roixmlfn, result.roirawfn, result.outfn)

if __name__ == "__main__":
  main()
