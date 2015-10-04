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

# convertTo.py
# Created by Disa Mhembere
# Email: dmhembe1@jhu.edu

"""
A module to load and convert graphs and invariant data between mat, npy and csv format
"""

import numpy as np
import os
import igraph
from computation.utils.csc_to_igraph import csc_to_igraph
from computation.utils.file_util import loadAnyMat
from computation.utils.attredge_adapter import attredge_to_igraph

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
    elif informat == "attredge":
      g = attredge_to_igraph(gfn)
    else:
      err_msg = "[ERROR]: Unknown format '%s'. Please check format and retry!" % informat
      print err_msg
      return (None, err_msg)
  except Exception, err_msg:
    print err_msg
    return (None, "[ERROR]: "+str(err_msg))

  out_err_msg = ""
  fn = ""
  for fmt in outformats:
    if fmt in ["graphml", "ncol", "edgelist", "lgl", "pajek", "dot", "gml", "leda"]:
      fn = os.path.join(save_dir, os.path.splitext(os.path.basename(gfn))[0]+"."+fmt)
      print "Writing converted file %s ..." % fn
      g.write(fn, format=fmt)
    else:
      out_err_msg += "File conversion format '%s' unknown and omitted ...\n" % fmt

  return (fn, out_err_msg)
