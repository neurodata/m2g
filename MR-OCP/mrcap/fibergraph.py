
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
    mask - TODO: Unused
    """
    raise NotImplementedError("Constructor should be implemented!")

  def add (self, fiber):
    """
    Add the edges to the graph found by obtaining all tracts with the fiber

    Positional arguments:
    ====================
    fiber - the fiber read fiber tract .dat file
    """
    roi_edges = itertools.combinations((fiber.getVids(self.rois)),2)

    for list_item in roi_edges:
      self.edge_dict[tuple(sorted(list_item))] += 1

  def complete (self):
    """
    Done adding fibers. Add edges and edge weights to the igraph
    """
    start = time()
    print "Adding %d edges to the graph ..." % len(self.edge_dict)
    self.spcscmat += self.edge_dict.keys()
    print "Completed adding edges in %.3f sec" % (time() - start)

    start = time()
    print "Adding edge weight to the graph ..."
    self.spcscmat.es["weight"] = self.edge_dict.values()
    print "Completed adding edge weight in %.3f sec" % (time() - start)
    self.spcscmat["region"] = "brain"
    self.spcscmat["sensor"] = "Magnetic Resonance"
    self.spcscmat["source"] = "http://openconnecto.me/graph-services"
    self.spcscmat["DOI"] = "10.1109/GlobalSIP.2013.6736878" # Migraine paper

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
    self.spcscmat.save(filename, format=gformat)

  def loadFromIgraph(self, filename, gformat="graphml"):
    """
    Load a sparse matrix from igraph as a numpy pickle

    Positional arguments:
    ====================
    filename - the file name/path to where you want to save the graph
    gformat - the format which you want to use to save the graph. Choices:
    """
    self.spcscmat = igraph.load(filename, format=gformat)
