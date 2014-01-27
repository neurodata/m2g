#!/usr/bin/python

# check_fibers.py
# Created by Disa Mhembere on 2014-01-27.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
from computation.utils.loadAdjMatrix import loadAnyMat
import scipy.io as sio
import numpy as np
from mrcap.zindex import MortonXYZ
import os

def check_graph(g_fn):
  limits = (182, 218, 182) # HARD-CODED BOUNDS
  g = loadAnyMat(g_fn)

  vset = set()
  fset = set()

  nonzero = g.nonzero()
  LEN_NNZ = nonzero[1].shape[0]

  print "Adding nnz vertices to set ..."
  for idx in xrange(LEN_NNZ):
    vset.add(nonzero[0][idx])
    vset.add(nonzero[1][idx])

    if idx%100000==0:
      print "Processed %d/%d ..." % (idx, LEN_NNZ)


  print "Checking if vertices are outside labels ..."
  for cnt, vertex in enumerate(vset):
    x, y, z = MortonXYZ(vertex)

    if x > limits[0] or y > limits[1] or z > limits[2]:
      print "Vertex %d has fibers and is outside the label mask ..." % vertex
      fset.add(vertex)

    if cnt%100000==0:
      print "Processed %d/%d ..." % (cnt, len(vset))

  if fset:
    print "Writing vertices to disk ..."
    f = open(os.path.splitext(os.path.basename(g_fn))[0]+".json", "wb")
    f.write(str(list(fset)))
    f.close()

  else:
    print "No vertices outside the label mask!"


def main():
  parser = argparse.ArgumentParser(description="Check if a MAT file has fibers (edges) outside the 'label' mask")
  parser.add_argument("graphfn", action="store", help="MATLAB matrix - adjacency matrix i.e. .mat format")
  result = parser.parse_args()

  check_graph(result.graphfn)

if __name__ == "__main__":
  main()