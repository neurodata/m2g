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

# graph.py
# Created by Greg Kiar on 2016-01-27.
# Email: gkiar@jhu.edu

from itertools import combinations
import numpy as np
import igraph as ig
import nibabel as nb


class graph(object):
    def __init__(self, N, rois, attr=None):
        """
        Initializes the graph with nodes corresponding to the number of ROIs

        **Positional Arguments:**

                N:
                    - Number of rois
                rois:
                    - Set of ROIs as either an array or niftii file)
                attr:
                    - Node or graph attributes. Can be a list. If 1 dimensional
                      will be interpretted as a graph attribute. If N
                      dimensional will be interpretted as node attributes. If
                      it is any other dimensional, it will be ignored.
        """
        self.N = N
        # TODO GK: support loading rois images
        self.rois = rois  # currently only supports niftis

        # TODO GK: make empty graph with N nodes, attribute 'id' = rois list
        # self.graph = ig.Graph.Erdos_Renyi(N, 0.3) # making random g for tests
        # self.graph.vs['name'] = range(N) # with random attrs
        # self.graph.vs['size'] = 2*range(N)
        pass

    def make_graph(self, streamlines, attr=None):
        """
        Takes streamlines and produces a graph

        **Positional Arguments:**

                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """
        g = np.zeros((self.N, self.N))
        templabel = nb.load(self.rois)
        label = templabel.get_data()

        print "# of Streamlines: " + str(np.shape(streamlines)[0])

        for y in range(np.shape(streamlines)[0]):
            if (y % 25000) == 0:
                print y

            ss = (np.round(streamlines[y]))
            ss = ss.astype(int)
            f = []

            for x in range(ss.shape[0]):
                f.append(label[ss[x][0], ss[x][1], ss[x][2]])

            f = np.unique(f)
            f = f[f != 0]
            ff = list(combinations(f, 2))

            for z in range(np.shape(ff)[0]):
                g[ff[z][0]-1, ff[z][1]-1] = g[ff[z][0]-1, ff[z][1]-1] + 1

        self.g = ig.Graph.Weighted_Adjacency(list(g), mode='undirected',
                                             attr='weight')
        self.g.vs['ids'] = np.unique(label)[np.unique(label) > 0]

        pass

    def get_graph(self):
        """
        Returns the graph object created
        """
        try:
            return self.g
        except AttributeError:
            print "Error: the graph has not yet been defined."
            pass

    def save_graph(self, graphname, fmt='graphml'):
        """
        Saves the graph to disk

        **Positional Arguments:**

                graphname:
                    - Filename for the graph

        **Optional Arguments:**

                fmt:
                    - Output graph format
        """
        self.g.save(graphname, format=fmt)
        pass

    def summary(self):
        """
        User friendly wrapping and display of graph properties
        """
        print "Graph attributes: " +\
              ("None" if len(self.g.attributes()) is 0
               else ", ".join([str(x) for x in self.g.attributes()]))

        print "Number of nodes: " + str(self.g.vcount())
        print "Node attributes: " +\
              ("None" if len(self.g.vs.attributes()) is 0
               else ", ".join([str(x) for x in self.g.vs.attributes()]))

        print "Number of edges: " + str(self.g.ecount())
        print "Edge attributes: " +\
              ("None" if len(self.g.es.attributes()) is 0
               else ", ".join([str(x) for x in self.g.es.attributes()]))
        pass
