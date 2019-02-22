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
# Repackaged by Derek Pisner on 2019-02-19
# Originally created by Greg Kiar on 2016-01-27.
# Email: dpisner@utexas.edu

from __future__ import print_function
import warnings
warnings.simplefilter("ignore")
from itertools import combinations, product
from collections import defaultdict
import numpy as np
import networkx as nx
import nibabel as nib
import ndmg
import time
import os

class graph_tools(object):
    def __init__(self, rois, tracks, affine, namer, connectome_path, attr=None, sens="dwi"):
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
	self.roi_file = rois
	self.roi_img = nib.load(self.roi_file)
        self.rois = self.roi_img.get_data().astype('int')
        n_ids = np.unique(self.rois)
        self.n_ids = n_ids[n_ids > 0]
        self.N = len(self.n_ids)
        self.modal = sens
	self.tracks = tracks
	self.affine = affine
	self.namer = namer
	self.connectome_path = connectome_path
        pass

    def make_regressors(self, attr=None):
	from nilearn.image import new_img_like
        import pandas as pd

        def get_parcel_list(parlistfile):
            bna_img = nib.load(parlistfile)
            bna_data = np.round(bna_img.get_data(),1)
            bna_data_for_coords_uniq = np.unique(bna_data)
            par_max = len(bna_data_for_coords_uniq) - 1
            bna_data = bna_data.astype('int16')
            img_stack = []
            for idx in range(1, par_max+1):
                roi_img = bna_data == bna_data_for_coords_uniq[idx].astype('int16')
                roi_img = roi_img.astype('int16')
                img_stack.append(roi_img)
            img_stack = np.array(img_stack).astype('int16')
            img_list = []
            for idy in range(par_max):
                roi_img_nifti = new_img_like(bna_img, img_stack[idy])
                img_list.append(roi_img_nifti)
            return(img_list)

        self.img_list = get_parcel_list(self.roi_file)

        print('Compiling voxel coordinates of all streamlines...')
        self.points = []
        for _, streamline in enumerate(self.tracks):
            point_set = np.round(streamline).astype('int')
            for point in point_set:
                self.points.append(tuple(point))

        print('Counting fiber waytotals and # voxels for each ROI...')
        fibers = {}
        rois = {}
        img_ix = 0
        for img in self.img_list:
            data = img.get_data()
            img_ix = img_ix + 1
            rois[img_ix] = np.sum(data.astype('bool'))
            for point in set(self.points):
                try:
                    loc = data[point[0], point[1], point[2]]
                except:
                    loc = None
                    pass
                if loc:
                    try:
                        fibers[img_ix] = fibers[img_ix] + 1
                    except:
                        fibers[img_ix] = 1
		else:
		    continue
            try:
                fibers[img_ix]
            except:
                fibers[img_ix] = 0
            print(str(img_ix) + ': Fibers - ' + str(fibers[img_ix]) + '  Voxels: ' + str(rois[img_ix]))

        self.df_regressors = pd.DataFrame({'fiber_count':pd.Series(fibers), 'roi_size':pd.Series(rois)})
	self.df_out = self.namer.name_derivative(self.connectome_path, "roi_regressors.csv")
	self.df_regressors.to_csv(self.df_out, sep='\t')

        return

    def make_graph_old(self, attr=None):
        """
        Takes streamlines and produces a graph
        **Positional Arguments:**
                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """
	print('Building connectivity matrix...')
	self.g = nx.Graph(name="Generated by NeuroData's MRI Graphs (ndmg)",
                          date=time.asctime(time.localtime()),
                          source="http://m2g.io",
                          region="brain",
                          sensor=self.modal,
                          ecount=0,
                          vcount=len(self.n_ids)
                          )
        print(self.g.graph)

        [self.g.add_node(ids) for ids in self.n_ids]

        nlines = np.shape(self.tracks)[0]
        print("# of Streamlines: " + str(nlines))

        for idx, streamline in enumerate(self.tracks):
            if (idx % int(nlines*0.05)) == 0:
                print(idx)

            points = np.round(streamline).astype(int)
            p = set()
            for point in points:
                try:
                    loc = self.rois[point[0], point[1], point[2]]
                except IndexError:
                    pass
                else:
                    pass

                if loc:
                    p.add(loc)

            edges = combinations(p, 2)
            for edge in edges:
                lst = tuple([int(node) for node in edge])
                self.edge_dict[tuple(sorted(lst))] += 1

        edge_list = [(k[0], k[1], v) for k, v in self.edge_dict.items()]
        self.g.add_weighted_edges_from(edge_list)
	return self.g

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

    def save_graph(self, graphname, fmt='igraph'):
        """
        Saves the graph to disk

        **Positional Arguments:**

                graphname:
                    - Filename for the graph
        """
        self.g.graph['ecount'] = nx.number_of_edges(self.g)
        self.g = nx.convert_node_labels_to_integers(self.g, first_label=1)
	print(self.g.graph)
        if fmt == 'edgelist':
            nx.write_weighted_edgelist(self.g, graphname, encoding='utf-8')
        elif fmt == 'gpickle':
            nx.write_gpickle(self.g, graphname)
        elif fmt == 'graphml':
            nx.write_graphml(self.g, graphname)
	elif fmt == 'txt':
	    np.savetxt(graphname, nx.to_numpy_matrix(self.g))
        elif fmt == 'npy':
            np.save(graphname, nx.to_numpy_matrix(self.g))
	elif fmt == 'igraph':
	    if self.modal == 'dwi':
                nx.write_weighted_edgelist(self.g, graphname, delimiter=" ", encoding='utf-8')
            elif self.modal == 'func':
                np.savetxt(graphname, self.g, comments='', delimiter=',', header=','.join([str(n) for n in self.n_ids]))
            else:
                raise ValueError("Unsupported Modality.")
        else:
            raise ValueError('Only edgelist, gpickle, and graphml currently supported')
        pass

    def summary(self):
        """
        User friendly wrapping and display of graph properties
        """
        print("\nGraph Summary:")
        print(nx.info(self.g))
        pass
