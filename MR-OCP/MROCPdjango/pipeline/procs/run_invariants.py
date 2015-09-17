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

#!/usr/bin/env python

# run_invariants.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import computation.composite.invariants as cci

def run_invariants(inv_list, graph_fn, save_dir, graph_format="graphml", sep_save=False):
  '''
  Run the selected multivariate invariants as defined

  @param inv_list: the list of invariants we are to compute
  @param graph_fn: the graph filename on disk
  @param save_dir: the directory where to save resultant data

  @param graph_format: the format of the graph
  @param sep_save: boolean on whether to save invariants in separate files
  '''
  inv_dict = {'graph_fn':graph_fn, 'save_dir':save_dir}
  for inv in inv_list:
    inv_dict[inv] = True

  inv_dict = cci.compute(inv_dict, sep_save=sep_save, gformat=graph_format)

  if isinstance(inv_dict, str):
    return inv_dict # Error message
  else:
    inv_dict = inv_dict[1]

  return_dict = dict()

  for key in inv_dict:
    if key.endswith("_fn") and not key.startswith("eig"): # skip eigs
      return_dict[key] = inv_dict[key]

  if inv_dict.get("eigvl_fn", None): # or "eigvect_fn"
    return_dict["eig"] = [inv_dict["eigvect_fn"], inv_dict["eigvl_fn"]] # Note this

  return return_dict

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()


if __name__ == "__main__":
  main()
