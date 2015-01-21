#!/usr/bin/python

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


# loadAdjMatrix.py
# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012

"""
Load up an adjacency matrix given G_fn, lcc & roiRoot
"""
import os
import argparse
import mrcap.lcc as lcc

import sys
from time import time
import scipy.io as sio
from computation.utils.file_util import loadAnyMat

def loadAdjMat(G_fn, lcc_fn):
  """
  Load adjacency matrix given lcc_fn & G_fn. lcc has z-indicies corresponding to the lcc.

  positional args:
  ================
  G_fn - the .mat file holding graph
  lcc_fn - the largest connected component .npy z-ordering

  returns:
  =======
  G_lcc - The largest connected component of a graph
  """

  start = time()
  print "Loading adjacency matrix..."
  try:
    vcc = lcc.ConnectedComponent(fn = lcc_fn) # creates conn_comp array
    G_full = loadAnyMat(G_fn) # sio.loadmat(G_fn)['fibergraph'] # load the full sparse graph

    G_lcc = vcc.induced_subgraph(G_full) # sparse graph of LCC

    G_lcc = G_lcc + G_lcc.T # Symmetrize
    print "Time to load Symmetrized LCC: %s secs" % (time()-start)
    return G_lcc

  except Exception, err:

    if not os.path.exists(lcc_fn):
      print "[IOError]: Lcc: %s Doesn't exist" % lcc_fn
      sys.exit(-1)

    if not os.path.exists(G_fn):
      print "[IOError]: Graph: %s Doesn't exist" % G_fn
      sys.exit(-1)

    else:
      print Exception, err
      raise Exception

def main():
  """
  CL parser and main runner
  """

  parser = argparse.ArgumentParser(description='Calculate Max Avg Degree estimate as max eigenvalue for biggraphs')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')

  result = parser.parse_args()
  loadAdjMat(result.G_fn, result.lcc_fn)

if __name__ == '__main__':
  main()