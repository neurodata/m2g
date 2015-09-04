
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

from time import time
import math
import itertools
from collections import defaultdict

import numpy as np
import igraph

from mrcap.fiber import Fiber
import mrcap.roi as roi
import zindex

# Abstract class for big and small fibergraphs

class _FiberGraph(object):
  def __init__(self, matrixdim, rois):
    """
    Unimplemented constructor for the abstract class for reading and creating
    fibergraphs.

    Positional arguments:
    =====================
    matrixdim - number of nodes in the graph
    rois - the region of interest of the brain masking
    """
    # Regions of interest
    self.rois = rois
    self.edge_dict = defaultdict(int) # Will have key=(v1,v2), value=weight

    # ======================================================================== #
    # make new igraph with adjacency matrix to be (maxval X maxval)
    self.graph = igraph.Graph(n=(int(self.rois.data.max()) + 1), directed=False)

  def add (self, fiber):
    """
    Add the edges to the graph found by obtaining all tracts with the fiber

    Positional arguments:
    ====================
    fiber - the fiber read fiber tract .dat file
    """
    roi_edges = itertools.combinations((fiber.get_vids(self.rois)),2)

    for list_item in roi_edges:
      self.edge_dict[tuple(sorted(list_item))] += 1

  def complete (self):
    """
    Done adding fibers. Add edges and edge weights to the igraph
    """
    start = time()
    print "Adding %d edges to the graph ..." % len(self.edge_dict)

    self.graph += self.edge_dict.keys()
    print "Completed adding edges in %.3f sec" % (time() - start)

    start = time()
    print "Adding edge weight to the graph ..."
    self.graph.es["weight"] = self.edge_dict.values()
    print "Completed adding edge weight in %.3f sec" % (time() - start)
    self.graph["region"] = "brain"
    self.graph["sensor"] = "Magnetic Resonance"
    self.graph["source"] = "http://openconnecto.me/graph-services"
    self.graph["DOI"] = "10.1109/GlobalSIP.2013.6736878" # Migraine paper

    print "Deleting zero-degree nodes..."
    zero_deg_nodes = np.where( np.array(self.graph.degree()) == 0 )[0]
    self.graph.delete_vertices(zero_deg_nodes)

    # Annotate graph with ecount and vcount for ingest speed
    self.graph["vcount"] = self.graph.vcount()
    self.graph["ecount"] = self.graph.ecount()

    print "Graph summary:"
    print self.graph.summary()
    print

  def saveToIgraph(self, filename, gformat="graphml"):
    """
    Save igraph to disk in specified format

    Positional arguments:
    ====================
    filename - the file name/path to where you want to save the graph
    gformat - the format which you want to use to save the graph. Choices:
    "graphml", "dot", "pajek" and those found at: http://igraph.sourceforge.net/doc/python/index.html
    """
    from os.path import splitext
    if not splitext(filename)[1][1:] == gformat:
      filename+=("."+gformat)
      print "Graph name adapted to '%s' ..." % filename

    print "Saving graph '%s' to disk ... " % filename
    self.graph.save(filename, format=gformat)

  def loadFromIgraph(self, filename, gformat="graphml"):
    """
    Load a sparse matrix from igraph as a numpy pickle

    Positional arguments:
    ====================
    filename - the file name/path to where you want to save the graph
    gformat - the format which you want to use to save the graph. Choices:
    """
    self.graph = igraph.load(filename, format=gformat)
