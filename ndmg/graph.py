#!/usr/bin/env python

"""
ndmg.graph
~~~~~~~~~~

Contains the primary functionality for connectome estimation after tractography has completed.
Used in the final stage of the pipeline.
"""


# standard library imports
import os
import time
from itertools import combinations
from collections import defaultdict

# package imports
import numpy as np
import networkx as nx
import nibabel as nib
from dipy.tracking._utils import _mapping_to_voxel, _to_voxel_coordinates
from itertools import combinations
from collections import defaultdict
from ndmg.utils.gen_utils import timer
import matplotlib

matplotlib.use("agg")
from matplotlib import pyplot as plt
from graspy.utils import ptr
from graspy.plot import heatmap


class GraphTools:
    """Initializes the graph with nodes corresponding to the number of ROIS

    Parameters
    ----------
    rois : str
        Path to a set of ROIs as either an array or nifti file
    tracks : list
        Streamlines for analysis
    affine : ndarray
        a 2-D array with ones on the diagonal and zeros elsewhere (DOESN'T APPEAR TO BE Used)
    namer : NameResource
        NameResource object containing relevant path for the pipeline
    connectome_path : str
        Path for the output connectome file (.ssv file)
    attr : [type], optional
        Node or graph attributes. Can be a list. If 1 dimensional, will be interpretted as a graph attribute. If N dimensional
        will be interpretted as node attributes. If it is any other dimensional, it will be ignored, by default None
    sens : str, optional
        type of MRI scan being analyzed (can be 'dwi' or 'func'), by default "dwi"

    Raises
    ------
    ValueError
        graph saved with unsupported igraph modality
    ValueError
        graph saved not using edgelist, gpickle, or graphml
    """

    def __init__(
        self, rois, tracks, affine, namer, connectome_path, attr=None, sens="dwi"
    ):

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

    @timer
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

    @timer
    def make_graph(self, error_margin=2, overlap_thr=1, voxel_size=2):
        """Takes streamlines and produces a graph using Numpy functions

        Parameters
        ----------
        error_margin : int, optional
            Number of mm around roi's to use (i.e. if 2, then any voxel within 2 mm of roi is considered part of roi), by default 2
        overlap_thr : int, optional
            The amount of overlap between an roi and streamline to be considered a connection, by default 1
        voxel_size : int, optional
            Voxel size for roi/streamlines, by default 2

        Returns
        -------
        Graph
            networkx Graph object containing the connectome matrix
        """
        print("Building connectivity matrix...")

        # Instantiate empty networkX graph object & dictionary
        # Create voxel-affine mapping
        lin_T, offset = _mapping_to_voxel(
            np.eye(4)
        )  # TODO : voxel_size was removed in dipy 1.0.0, make sure that didn't break anything when voxel size is not 2mm
        mx = len(np.unique(self.rois.astype(np.int64))) - 1
        self.g = nx.Graph(ecount=0, vcount=mx)
        edge_dict = defaultdict(int)
        node_dict = dict(
            zip(np.unique(self.rois).astype("int16") + 1, np.arange(mx) + 1)
        )

        # Add empty vertices
        for node in range(1, mx + 1):
            self.g.add_node(node)

        nlines = np.shape(self.tracks)[0]
        print("# of Streamlines: " + str(nlines))

        ix = 0
        for s in self.tracks:
            # Map the streamlines coordinates to voxel coordinates and get labels for label_volume
            # i, j, k = np.vstack(np.array([get_sphere(coord, error_margin,
            #                                          (voxel_size, voxel_size, voxel_size),
            #                                          self.roi_img.shape) for coord in
            #                               _to_voxel_coordinates(s, lin_T, offset)])).T

            # Map the streamlines coordinates to voxel coordinates
            points = _to_voxel_coordinates(s, lin_T, offset)

            # get labels for label_volume
            i, j, k = points.T

            lab_arr = self.rois[i, j, k]
            endlabels = []
            for lab in np.unique(lab_arr).astype("int16"):
                if (lab > 0) and (np.sum(lab_arr == lab) >= overlap_thr):
                    endlabels.append(node_dict[lab])

            edges = combinations(endlabels, 2)
            for edge in edges:
                lst = tuple([int(node) for node in edge])
                edge_dict[tuple(sorted(lst))] += 1

            edge_list = [(k[0], k[1], v) for k, v in edge_dict.items()]

            self.g.add_weighted_edges_from(edge_list)
            ix = ix + 1

        conn_matrix = np.array(nx.to_numpy_matrix(self.g))
        conn_matrix[np.isnan(conn_matrix)] = 0
        conn_matrix[np.isinf(conn_matrix)] = 0
        conn_matrix = np.asmatrix(np.maximum(conn_matrix, conn_matrix.transpose()))
        g = nx.from_numpy_matrix(conn_matrix)

        return g

    def save_graph(self, graphname, fmt="igraph"):
        """Saves the graph to disk

        Parameters
        ----------
        graphname : str
            Filename for the graph
        fmt : str, optional
            Format you want the graph saved as [edgelist, gpickle, graphml, txt, npy, igraph], by default "igraph"

        Raises
        ------
        ValueError
            Unsupported modality (not dwi or func) for saving the graph in igraph format
        ValueError
            Unsupported format
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
            nx.write_weighted_edgelist(
                self.g, graphname, delimiter=" ", encoding="utf-8"
            )
        else:
            raise ValueError(
                "Only edgelist, gpickle, graphml, txt, and npy are currently supported"
            )

    def save_graph_png(self, graphname):
        """Saves adjacency graph, made using graspy's heatmap function, as a png. This will be saved in the qa/graphs_plotting/ directory

        Parameters
        ----------
        graphname : str
            name of the generated graph (do not include '.png')
        """

        conn_matrix = np.array(nx.to_numpy_matrix(self.g))
        conn_matrix = ptr.pass_to_ranks(conn_matrix)
        heatmap(conn_matrix)
        plt.savefig(
            self.namer.dirs["qa"]["graphs_plotting"]
            + "/"
            + graphname.split(".")[:-1][0].split("/")[-1]
            + ".png"
        )
        plt.close()

    def summary(self):
        """
        User friendly wrapping and display of graph properties
        """
        print("\nGraph Summary:")
        print(nx.info(self.g))
        pass
