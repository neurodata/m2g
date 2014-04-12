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

def create(roixmlfn, roirawfn, baseatlasfn):
  #nifti_base = nib.load(baseatlasfn)

  print "Loading rois as base ..."
  #roix = roi.ROIXML(roixmlfn) # Create object of type ROIXML
  base = roi.ROIData (roirawfn, roi.ROIXML(roixmlfn).getShape()).data
  new = np.zeros_like(base)
  
  # Labelling new 
  label_used = False
  print "Labeling new ..."
  region_num = 1
  for z in xrange(1, base.shape[2]-1, 3):
    for y in xrange(1, base.shape[1]-1, 3):
      for x in xrange(1, base.shape[0]-1, 3):

        if True: #label_used: 
          region_num += 1 # only increase counter when a label was used
          label_used = False

        # set other (3*3)-1 around me to same region
        for zz in xrange(-1,2):
          for yy in xrange(-1,2):
            for xx in xrange(-1,2):
            #try:
              if (base[x+xx,y+yy,z+zz]): # Masking
                label_used = True
                new[x+xx,y+yy,z+zz] = region_num
            #except Exception as e:
              #print "Failed to add index: [%d,%d,%d] with value %d" % (x+xx,y+yy,z+zz, region_num)

  import pdb; pdb.set_trace()
def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("roixmlfn", action="store", help="")
  parser.add_argument("roirawfn", action="store", help="")
  parser.add_argument("baseatlasfn", action="store", help="")
  result = parser.parse_args()

  create(result.roixmlfn, result.roirawfn, result.baseatlasfn)

if __name__ == "__main__":
  main()
