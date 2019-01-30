#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
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

from __future__ import print_function

from itertools import product
from collections import defaultdict
import numpy as np
import networkx as nx
import nibabel as nb
import ndmg
import time


class graph_tools(object):
    def __init__(self, rois, attr=None, sens="dmri"):
        """
        Initializes the graph with nodes corresponding to the number of ROIs

        **Positional Arguments:**
                rois:
                    - Set of ROIs as either an array or niftii file)
                attr:
                    - Node or graph attributes. Can be a list. If 1 dimensional
                      will be interpretted as a graph attribute. If N
                      dimensional will be interpretted as node attributes. If
                      it is any other dimensional, it will be ignored.
                sens: string, Default to 'dmri'
                    - sensor of acquisition. Can be 'dmri' or 'fmri'
        """
        self.edge_dict = defaultdict(int)

        self.rois = nb.load(rois).get_data().astype('int')
        n_ids = np.unique(self.rois)
        self.n_ids = n_ids[n_ids > 0]
        self.N = len(self.n_ids)
        self.modal = sens
        pass

    def make_graph(self, streamlines, attr=None):
        """
        Takes streamlines and produces a graph. Note that the parcellation is
        expected to be numbered from 0 to n, where n are the number of vertices.
        If any vertices are skipped, non-deterministic behavior may be expected.

        **Positional Arguments:**

                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """
        self.g, _ = utils.connectivity_matrix(self.tracks, self.rois,
        affine=self.dwi_img.affine, return_mapping=True, mapping_as_streamlines=True,
            symmetric=True)
        self.conn_matrix_filt = self.conn_matrix[1:self.N, 1:self.N]
        return self.conn_matrix_symm

    def cor_graph(self, timeseries, attr=None):
        """
        Takes timeseries and produces a correlation matrix

        **Positional Arguments:**
            timeseries:
                -the timeseries file to extract correlation for
                dimensions are [numrois]x[numtimesteps]
        """
        ts = timeseries[0]
        rois = timeseries[1]
        print("Estimating absolute correlation matrix for {} ROIs...".format(len(rois)))
        self.g = np.abs(np.corrcoef(ts))  # calculate abs pearson correlation
        self.g = np.nan_to_num(self.g).astype(object)
        self.n_ids = rois
        return self.g        

    def get_graph(self):
        """
        Returns the graph object created
        """
        try:
            return self.g
        except AttributeError:
            print("Error: the graph has not yet been defined.")
            pass

    def as_matrix(self):
        """
        Returns the graph as a matrix.
        """
        g = self.get_graph()
        return nx.to_numpy_matrix(g, nodelist=np.sort(g.nodes()).tolist())

    def save_graph(self, graphname):
        """
        Saves the graph to disk

        **Positional Arguments:**

                graphname:
                    - Filename for the graph
        """
        np.savetxt(graphname, self.g, comments='', delimiter=',',
            header=','.join([str(n) for n in self.n_ids]))
        pass

    def summary(self):
        """
        User friendly wrapping and display of graph properties
        """
        print("\n Graph Summary:")
        print(nx.info(self.g))
        pass
