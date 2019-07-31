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


import warnings

warnings.simplefilter("ignore")
import numpy as np
import networkx as nx
import nibabel as nib
import time
import os
from dipy.tracking._utils import (_mapping_to_voxel, _to_voxel_coordinates)
from itertools import combinations
from collections import defaultdict


def get_sphere(coords, r, vox_dims, dims):
    """
    Return all points within r mm of coords. Generates a cube and then discards all points outside sphere.

    Parameters
    ----------
    coords : list
        List of (x, y, z) tuples corresponding to a coordinate atlas used or
        which represent the center-of-mass of each parcellation node.
    r : int
        Radius for sphere.
    vox_dims : array/tuple
        1D vector (x, y, z) of mm voxel resolution for sphere.
    dims : array/tuple
        1D vector (x, y, z) of image dimensions for sphere.

    Returns
    -------
    neighbors : list
        A list of indices, within the dimensions of the image, that fall within a spherical neighborhood defined by
        the specified error radius of the list of the input coordinates.

    References
    ----------
    .. Adapted from NeuroSynth
    """
    r = float(r)
    xx, yy, zz = [slice(-r / vox_dims[i], r / vox_dims[i] + 0.01, 1) for i in range(len(coords))]
    cube = np.vstack([row.ravel() for row in np.mgrid[xx, yy, zz]])
    sphere = cube[:, np.sum(np.dot(np.diag(vox_dims), cube) ** 2, 0) ** .5 <= r]
    sphere = np.round(sphere.T + coords)
    neighbors = sphere[(np.min(sphere, 1) >= 0) & (np.max(np.subtract(sphere, dims), 1) <= -1), :].astype(int)
    return neighbors

class graph_tools(object):
    def __init__(
        self, rois, tracks, affine, namer, connectome_path, attr=None, sens="dwi"
    ):
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
        self.rois = self.roi_img.get_data().astype("int")
        self.n_ids = self.rois[self.rois > 0]
        self.N = len(self.n_ids)
        self.modal = sens
        self.tracks = tracks
        self.affine = affine
        self.namer = namer
        self.connectome_path = os.path.dirname(connectome_path)
        pass

    def make_graph_old(self):
        """
        Takes streamlines and produces a graph
        **Positional Arguments:**
                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """
        print("Building connectivity matrix...")
        self.g = nx.Graph(
            name="Generated by NeuroData's MRI Graphs (ndmg)",
            date=time.asctime(time.localtime()),
            source="http://m2g.io",
            region="brain",
            sensor=self.modal,
            ecount=0,
            vcount=len(self.n_ids),
        )
        print(self.g.graph)

        [self.g.add_node(ids) for ids in self.n_ids]

        nlines = np.shape(self.tracks)[0]
        print("# of Streamlines: " + str(nlines))

        for idx, streamline in enumerate(self.tracks):
            if (idx % int(nlines * 0.05)) == 0:
                print(idx)

            points = np.round(streamline).astype(int)
            p = set()
            for point in points:
                try:
                    loc = self.rois[point[0], point[1], point[2]]
                except IndexError:
                    loc = ""
                    pass

                if loc:
                    p.add(loc)
                else:
                    pass

            edges = combinations(p, 2)
            for edge in edges:
                lst = tuple([int(node) for node in edge])
                self.edge_dict[tuple(sorted(lst))] += 1

        edge_list = [(k[0], k[1], v) for k, v in list(self.edge_dict.items())]
        self.g.add_weighted_edges_from(edge_list)
        return self.g, self.edge_dict

    def make_graph(self, error_margin=2, overlap_thr=1, voxel_size=2):
        """
        Takes streamlines and produces a graph
        **Positional Arguments:**
                streamlines:
                    - Fiber streamlines either file or array in a dipy EuDX
                      or compatible format.
        """
        print("Building connectivity matrix...")

        # Instantiate empty networkX graph object & dictionary
        # Create voxel-affine mapping
        lin_T, offset = _mapping_to_voxel(np.eye(4), voxel_size)
        mx = len(np.unique(self.rois.astype(np.int64)))
        self.g = nx.Graph(ecount=0, vcount=mx)
        edge_dict = defaultdict(int)
        node_dict = dict(zip(np.unique(self.rois)[1:], np.arange(mx)[1:]))

        # Add empty vertices
        for node in range(mx):
            self.g.add_node(node)

        nlines = np.shape(self.tracks)[0]
        print("# of Streamlines: " + str(nlines))

        ix = 0
        for s in self.tracks:
            # Map the streamlines coordinates to voxel coordinates
            points = _to_voxel_coordinates(s, lin_T, offset)

            points = np.array([get_sphere(coord, error_margin, (voxel_size, voxel_size, voxel_size), self.roi_img.shape) for coord in points])

            # get labels for label_volume
            i, j, k = points.T
            lab_arr = self.rois[i, j, k]
            endlabels = []
            for lab in np.unique(lab_arr):
                if lab > 0:
                    if np.sum(lab_arr == lab) >= overlap_thr:
                        endlabels.append(node_dict[lab])

            edges = combinations(endlabels, 2)
            for edge in edges:
                lst = tuple([int(node) for node in edge])
                edge_dict[tuple(sorted(lst))] += 1

            edge_list = [(k[0], k[1], v) for k, v in edge_dict.items()]

            self.g.add_weighted_edges_from(edge_list)
            ix = ix + 1

            conn_matrix = nx.to_numpy_array(self.g)
            conn_matrix[np.isnan(conn_matrix)] = 0
            conn_matrix[np.isinf(conn_matrix)] = 0
            conn_matrix = np.maximum(conn_matrix, conn_matrix.transpose())
            g = nx.from_numpy_array(conn_matrix)

        return g


    def cor_graph(self, timeseries):
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

    def save_graph(self, graphname, fmt="igraph"):
        """
        Saves the graph to disk

        **Positional Arguments:**

                graphname:
                    - Filename for the graph
        """
        self.g.graph["ecount"] = nx.number_of_edges(self.g)
        self.g = nx.convert_node_labels_to_integers(self.g, first_label=1)
        print(self.g.graph)
        if fmt == "edgelist":
            nx.write_weighted_edgelist(self.g, graphname, encoding="utf-8")
        elif fmt == "gpickle":
            nx.write_gpickle(self.g, graphname)
        elif fmt == "graphml":
            nx.write_graphml(self.g, graphname)
        elif fmt == "txt":
            np.savetxt(graphname, nx.to_numpy_matrix(self.g))
        elif fmt == "npy":
            np.save(graphname, nx.to_numpy_matrix(self.g))
        elif fmt == "igraph":
            if self.modal == "dwi":
                nx.write_weighted_edgelist(
                    self.g, graphname, delimiter=" ", encoding="utf-8"
                )
            elif self.modal == "func":
                np.savetxt(
                    graphname,
                    self.g,
                    comments="",
                    delimiter=",",
                    header=",".join([str(n) for n in self.n_ids]),
                )
            else:
                raise ValueError("Unsupported Modality.")
        else:
            raise ValueError("Only edgelist, gpickle, and graphml currently supported")
        pass

    def save_graph_png(self, graphname):
        import matplotlib
        matplotlib.use('agg')
        from matplotlib import pyplot as plt
        from nilearn.plotting import plot_matrix

        from sklearn.preprocessing import normalize
        conn_matrix = nx.to_numpy_array(self.g)
        conn_matrix = normalize(conn_matrix)
        [z_min, z_max] = -np.abs(conn_matrix).max(), np.abs(conn_matrix).max()
        plot_matrix(conn_matrix, figure=(10, 10), vmax=z_max * 0.5, vmin=z_min * 0.5, auto_fit=True, grid=False,
                    colorbar=False)
        plt.savefig(self.namer.dirs["qa"]['graphs_plotting'] + '/' + graphname.split('.')[:-1][0].split('/')[-1] +
                    '.png')
        plt.close()


    def summary(self):
        """
        User friendly wrapping and display of graph properties
        """
        print("\nGraph Summary:")
        print(nx.info(self.g))
        pass
