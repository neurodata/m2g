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

# max_avg_deg.py
# Created by Disa Mhembere on 2014-08-03.
# Email: disa@jhu.edu

from computation.utils.r_utils import r_igraph_set_graph_attribute
from computation.algs.eigen.eigen import r_igraph_eigs
from computation.utils.igraph_attributes import r_igraph_get_attr
from rpy2.rinterface import NULL

def r_igraph_max_ave_degree(g):
  """
  Compute local triangle count of graph g and save as necessary
  *Global graph attributes can only be stored in the graph*

  @param g: The igraph graph loaded via Rpy2 i.e. an R object

  @return: Same graph an input but with added invariant as an attribute
  """

  mad = r_igraph_get_attr(g, "eigvals", "g") # See if we already have computed eigenvalues for the graph
  if mad == NULL: # Ok then compute top 1 eig ourself
    mad = r_igraph_eigs(g, 1, return_eigs=True, save_fn=None)[0]
  else:
    mad = float(mad[0].split(",")[0][1:]) # The largest eigenvalue is held at index 0

  if mad is not None:
    g = r_igraph_set_graph_attribute(g, "max_ave_degree", mad)
  else: # More than likely ran out of memory
    print "Failed to estimate max ave degree because eigensolver failed ..."

  return g # return so we can use for other attributes
