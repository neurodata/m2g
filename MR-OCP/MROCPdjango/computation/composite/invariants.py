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

# invariants.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu

import os
import argparse
from time import time

from computation.utils.getBaseName import getBaseName
from computation.utils.file_util import loadAnyMat
from computation.utils.csc_to_igraph import csc_to_r_igraph
from computation.utils.r_utils import *

# Algorithms
from computation.algs.eigen.eigen import r_igraph_eigs
from computation.algs.max_avg_degree.max_avg_deg import r_igraph_max_ave_degree
from computation.algs.transitivity.transitivity import r_igraph_clust_coeff
from computation.algs.scan1stat.scan1 import r_igraph_scan1
from computation.algs.triangles.triangles import r_igraph_triangles
from computation.algs.degree.degree import r_igraph_degree

def compute(inv_dict, sep_save=True, gformat="graphml"):
  """
  Actual function that computes invariants and saves them to a location

  positional arguments:
  =====================

  inv_dict: is a dict that must contain:
    - inv_dict["graph_fn"]

  inv_dict: optional arguments:
    - inv_dict["edge"]: boolean for global edge count
    - inv_dict["ver"]: boolean for global vertex number
    - inv_dict["tri"]: boolean for local triangle count
    - inv_dict["eig"]: boolean for eigenvalues and eigenvectors
    - inv_dict["deg"]: boolean for local degree count
    - inv_dict["ss1"]: boolean for scan 1 statistic
    - inv_dict["cc"]: boolean for clustering coefficient
    - inv_dict["mad"]: boolean for maximum average degree
    - inv_dict["k]: the  number of eigenvalues to compute
    - inv_dict["save_dir"]: the base path where all invariants will create sub-dirs & be should be saved

  gformat - INPUT format of the graph

  optional arguments:
  ===================
  sep_save: boolean for auto save or not
  """

  if inv_dict.get("save_dir", None) is None:
   inv_dict["save_dir"] = os.path.join(os.path.dirname(inv_dict["graph_fn"]), "graphInvariants")

  if not os.path.exists(inv_dict["save_dir"]): os.makedirs(inv_dict["save_dir"])

  if inv_dict.has_key("G"):
    if inv_dict["G"] is not None:
      G = inv_dict["G"]
  else:
    try:
      if gformat in ["edgelist", "pajek", "ncol", "lgl", "graphml", "gml", "dot", "leda"]: #  All igraph supported formats
        G = r_igraph_load_graph(inv_dict["graph_fn"], gformat)
      elif gformat == "mat":
        G = csc_to_r_igraph(loadAnyMat(inv_dict['graph_fn']))

      if isinstance(G, str):
        return G # There was a loading error
    except Exception, err_msg:
      return str(err_msg)

  #============================ Call to invariants ============================#
  start = time()

  if inv_dict.get("eig", False) != False:

    if inv_dict.get("k") is None:
      inv_dict["k"] = min(100, r_igraph_vcount(G, False)-3) # Max of 100 eigenvalues

    # Test if graph is too big for invariants
    print "Computing eigen decompositon ..."
    
    lcc = True if r_igraph_ecount(G, False) > 500000 else False
    if sep_save:
      inv_dict["eigvl_fn"] = os.path.join(inv_dict["save_dir"], "Eigen", \
                                getBaseName(inv_dict["graph_fn"]) + "_eigvl.npy")
      inv_dict["eigvect_fn"] = os.path.join(inv_dict["save_dir"], "Eigen", \
                                getBaseName(inv_dict["graph_fn"]) + "_eigvect.npy")
      G = r_igraph_eigs(G, inv_dict['k'], save_fn=(inv_dict["eigvl_fn"], inv_dict["eigvect_fn"]), lcc=lcc)

    else: G = r_igraph_eigs(G, inv_dict['k'], save_fn=None, lcc=lcc)
    #else: G = r_igraph_eigs(G, 4, save_fn=None, lcc=True)

  if inv_dict.get("mad", False) != False:
    if r_igraph_vcount(G, False) < 1000000: # Cannot compute eigs on very big graphs
      if sep_save:
        inv_dict["mad_fn"] = os.path.join(inv_dict["save_dir"], "MAD", \
                                  getBaseName(inv_dict["graph_fn"]) + "_mad.npy")
      print "Computing MAD ..."
      G = r_igraph_max_ave_degree(G)
    else:
      print "Graph too big to compute spectral embedding"

  if inv_dict.get("ss1", False) != False:
    print "Computing Scan 1 ..."
    if sep_save:
      inv_dict["ss1_fn"] = os.path.join(inv_dict["save_dir"], "SS1", \
                                getBaseName(inv_dict["graph_fn"]) + "_scanstat1.npy")
    G = r_igraph_scan1(G, inv_dict.get("ss1_fn", None))

  if inv_dict.get("tri", False) != False:
    print "Computring triangle count ..."
    if sep_save:
      inv_dict["tri_fn"] = os.path.join(inv_dict["save_dir"], "Triangle", \
                                getBaseName(inv_dict["graph_fn"]) + "_triangles.npy")
    G = r_igraph_triangles(G, inv_dict.get("tri_fn", None))

  if inv_dict.get("cc", False) != False:
    print "Computing clustering coefficient .."
    if sep_save:
      inv_dict["cc_fn"] = os.path.join(inv_dict["save_dir"], "ClustCoeff",\
                                getBaseName(inv_dict["graph_fn"]) + "_clustcoeff.npy")
    G = r_igraph_clust_coeff(G, inv_dict.get("cc_fn", None))

  if inv_dict.get("deg", False) != False:
    print "Computing degree ..."
    if sep_save:
      inv_dict["deg_fn"] = os.path.join(inv_dict["save_dir"], "Degree",\
                                getBaseName(inv_dict["graph_fn"]) + "_degree.npy")
    G = r_igraph_degree(G, "total", inv_dict.get("deg_fn", None))

  # num edges
  if inv_dict.get("edge", False) != False:
    print "Computing global edge count ..."
    G = r_igraph_ecount(G, True)

  # num vertices
  if inv_dict.get("ver", False) != False:
    print "Computing global vertex count ..."
    G = r_igraph_vcount(G, True)

  print "Total invariant compute time = %.3fsec" % (time() - start)

  # Save graph with all new attrs
  inv_dict["out_graph_fn"] = os.path.join(inv_dict["save_dir"], os.path.splitext(os.path.basename(inv_dict["graph_fn"]))[0])
  if os.path.splitext(inv_dict["out_graph_fn"])[1][1:] != ".graphml": inv_dict["out_graph_fn"] += ".graphml"
  r_igraph_write(G, inv_dict["out_graph_fn"]) # ALL GRAPHS SAVED AS GRAPHML!

  return G, inv_dict

if __name__ == "__main__":

  # Added for -h flag
  parser = argparse.ArgumentParser(description="Script to run selected invariants")
  result =  parser.parse_args()

  print "Running test ...."
  inv_dict = {}

  inv_dict["G"] = r_create_test_graph()
  inv_dict["graph_fn"] = "testgraph.graphml" # dummy

  inv_dict["eig"] = True; inv_dict["k"] = 3;
  inv_dict["cc"] = True; inv_dict["ss1"] = True;
  inv_dict["tri"] = True; inv_dict["mad"] = True;
  inv_dict["ver"] =  True; inv_dict["edge"] = True; inv_dict["deg"] = True

  g = compute(inv_dict, sep_save=False)
