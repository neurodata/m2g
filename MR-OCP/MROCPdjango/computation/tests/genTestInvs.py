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


# Author: Disa Mhembere
# New version now compatible with composite refactored code to compute graph invariants and compare vs gold std as a unittest.
# Date: 3 December 2013

import argparse
import unittesting
import pdb
import numpy as np

# Invariant imports
from computation.composite.invariants import compute
###########
# TESTING #
###########

def testing(inv_dict):

  print "Entering testing module ..."
  inv_dict = compute(inv_dict)

  num_nodes = np.load(inv_dict["ver_fn"]).item()

  benchdir = "/Users/disa/MR-connectome/MROCPdjango/computation/tests/bench" # TODO DM: Alter Dynamically
  testObj = unittesting.test(inv_dict["graph_fn"], inv_dict["save_dir"], num_nodes, inv_dict["ss1_fn"]\
      , inv_dict["deg_fn"], inv_dict["tri_fn"], inv_dict["cc_fn"], inv_dict["mad_fn"], benchdir) # Create unittest object

  testObj.testClustCoeff()
  testObj.testDegree()
  testObj.testTriangles()
  testObj.testMAD()
  testObj.testSS1()

#########################  ************** #########################

def main():

  parser = argparse.ArgumentParser(description='Run graph invariant test on a graph')
  parser.add_argument('graph_fn', action='store',help='the full filename of the  \
                      CSC matrix representing a graph (.mat format) to have *NOTE DO NOT USE UNDERSCORES (_)\
                      in path leaf. eg. /foo/bar_bar/foo.mat is OK but /foo/bar/foo_bar.mat is NOT. [TODO fix]')
  #parser.add_argument('graphsize', action='store', help='graphsize [s|b]. s is for small and b is for big.')

  parser.add_argument('-D', '--data_elem', action='store', default=None, help='the name of the data element within the .mat matrix.')
  parser.add_argument('-S', '--save_dir', action='store', default= "./mrdata", help='the directory where the invariants \
                      are to be stored (each invariant will create its own subdirectory within this). \
                      The defualt is ./mrdata')

  # Invariant options
  parser.add_argument('-A', '--all', action='store_true', help='pass to compute ALL invariants')
  parser.add_argument('-d', '--deg', action='store_true', help='pass to compute local degree')
  parser.add_argument('-e', '--eig', action='store_true', help='pass to compute global top k eigenvalues & eigenvectors')
  parser.add_argument('-c', '--cc', action='store_true', help='pass to compute local clustering coefficient')
  parser.add_argument('-t', '--tri', action='store_true', help='pass to compute local triangle count')
  parser.add_argument('-s', '--ss1', action='store_true', help='pass to compute scan 1 statistic')
  parser.add_argument('-m', '--mad', action='store_true', help='pass to compute global max. average degree')
  parser.add_argument('-g', '--edge', action='store_true', help='pass to compute global egde count')
  parser.add_argument('-v', '--ver', action='store_true', help='pass to compute global vertex count')

  parser.add_argument('-ef', '--eigvl_fn', action='store', help='If the eigenvalue file \
                      already exists pass it in to avoid recomputing. Used for -m, -t, -c, -A')
  parser.add_argument('-tf', '--tri_fn', action='store', help='If triangle count file\
                      already exists, pass it in to avoid recomputing. Used for -c')
  parser.add_argument('-df', '--deg_fn', action='store', help='If degree count file\
                      already exists, pass it in to avoid recomputing. Used for -c')
  parser.add_argument('-lf', '--lcc_fn', action='store', help='If you have a pre-computed largest connected component (.npy format) file add full file name of it here')
  parser.add_argument('-l', '--lcc', action='store_true', help='Compute the largest connected component for the graph and use it in computations. [No need to select if you already have it pre-computed i.e used `-lf`]')

  parser.add_argument('-k', action='store', type = int, help='The number of eigenvalues to compute. Max is 100')

  result = parser.parse_args()
  result.graphsize = "big" if (result.lcc or result.lcc_fn) else "small"

  if result.all:
    for key in result.__dict__:
      if result.__dict__[key] == False:
        result.__dict__[key] = True

  testing(result.__dict__)

if __name__ == '__main__':
  main()