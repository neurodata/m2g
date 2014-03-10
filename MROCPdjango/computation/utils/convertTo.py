#!/usr/bin/python

# convertTo.py
# Created by Disa Mhembere
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

"""
A module to load and convert graphs and invariant data between mat, npy and csv format
"""

import numpy as np
import os
import igraph
from computation.utils.csc_to_igraph import csc_to_igraph
from computation.utils.file_util import loadAnyMat

def convert_graph(gfn, informat, save_dir, *outformats):
  """
  Convert between igraph supported formats. No conversion to MAT or NPY available.

  Positional arguments:
  ====================

  gfn - the graph file name
  informat - the input format of the graph
  save_dir - the directory where we save result to
  outformat - a list of output formats
  """
  try:
    if informat in ["graphml", "ncol", "edgelist", "lgl", "pajek", "graphdb"]:
      g = igraph.read(gfn, None)
    elif informat == "mat":
      g = csc_to_igraph(loadAnyMat(gfn))
    elif informat == "npy":
      g = csc_to_igraph(np.load(gfn).item())
    else:
      err_msg = "[ERROR]: Unknown format '%s'. Please check format and re-try!" % informat
      print err_msg
      return err_msg
  except Exception, err_msg:
    print err_msg
    return "[ERROR]: "+str(err_msg)

  out_err_msg = ""
  for fmt in outformats:
    if fmt in ["graphml", "ncol", "edgelist", "lgl", "pajek", "dot", "gml", "leda"]:
      fn = os.path.join(save_dir, os.path.splitext(os.path.basename(gfn))[0]+"."+fmt)
      print "Writing converted file %s ..." % fn
      g.write(fn, format=fmt)
    else:
      out_err_msg += "File conversion format '%s' unknown and omitted ...\n" % fmt

  return out_err_msg
