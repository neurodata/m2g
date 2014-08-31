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

# degree.py
# Created by Disa Mhembere on 2014-08-13.
# Email: disa@jhu.edu

import os
from computation.utils.file_util import createSave
import rpy2.robjects as robjects
from computation.utils.r_utils import r_igraph_set_vertex_attr

def r_igraph_degree(g, mode="total", save_fn=None):
  """
  Compute degree of graph g and save as necessary

  Positional arguments
  ====================
  g - The igraph loaded via Rpy2 so an R object

  Optional arguments
  ==================
  mode - the type of degree. Default is an undirected i.e. in-degree + out degree
  save_fn - the filename you want to use to save it. If not provided
  the graph adds a degree attribute to all nodes and returns.
  """

  deg = robjects.r("""
  require(igraph)
  fn <- function(g){
  igraph::degree(g, mode="%s")
  }
  """ % mode)
  degvector = deg(g)

  if save_fn:
    save_fn = os.path.abspath(save_fn)
    createSave(save_fn, degvector) # TODO: Clean input for programmatic access
    print "Degree saved as %s ..." % save_fn
  else:
    g = r_igraph_set_vertex_attr(g, "degree", degvector)  # Attribute name may need to change

  return g # return so we can use for other attributes
