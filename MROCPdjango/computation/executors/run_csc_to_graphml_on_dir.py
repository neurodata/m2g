#!/usr/bin/python

# run_csc_to_graphml_on_dir.py
# Created by Disa Mhembere on 2014-01-22.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

from paths import include
include()

import argparse
from computation.utils import graphml_adapter
from computation.utils.file_util import loadAnyMat
from glob import glob
import os

def main():
  parser = argparse.ArgumentParser(description="Convert a directory of CSC graphs to graphml format")
  parser.add_argument("directory", action="store", nargs="+", help="The directory(ies) we should run on. *Don't add '/' to end of dir name")
  parser.add_argument("-w", "--weighted", action="store_true", help="Pass flag if the graphs are weighted")
  result = parser.parse_args()

  for dircty in result.directory:
    new_dir = dircty+"_graphml"
    if not os.path.exists(new_dir): os.makedirs(new_dir); print "Making dir %s ..." % new_dir
    else: print "Dir %s already exists ..." % new_dir
    for fn in glob(os.path.join(dircty, "*.mat")):
      print "Converting %s ..." % fn
      new_fn = os.path.join(new_dir, os.path.splitext(os.path.basename(fn))[0]+".graphml")
      print "Creating %s ..." % new_fn
      graphml_adapter.csc_to_graphml(loadAnyMat(fn), is_weighted=result.weighted, desikan=True, is_directed=False, save_fn=new_fn)

if __name__ == "__main__":
  main()
