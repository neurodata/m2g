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

# graph_qc.py
# Created by Greg Kiar on 2016-05-11.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
from collections import OrderedDict
from subprocess import Popen
from scipy.stats import gaussian_kde
from ndmg.utils import loadGraphs
from ndmg.stats import plot_metrics

import numpy as np
import nibabel as nb
import networkx as nx
import pickle
import sys
import os


def compute_metrics(fs, outdir, atlas, verb=False):
    """
    Given a set of files and a directory to put things, loads graphs and
    performs set of analyses on them, storing derivatives in a pickle format
    in the desired output location.

    Required parameters:
        fs:
            - Dictionary of lists of files in each dataset
        outdir:
            - Path to derivative save location
        atlas:
            - Name of atlas of interest as it appears in the directory titles
    Optional parameters:
        verb:
            - Toggles verbose output statements
    """

    graphs = loadGraphs(fs, verb=verb)

    #  Number of non-zero edges (i.e. binary edge count)
    print("Computing: NNZ")
    nnz = OrderedDict((subj, len(nx.edges(graphs[subj]))) for subj in graphs)
    write(outdir, 'number_non_zeros', nnz, atlas) 

    #  Degree sequence
    print("Computing: Degree Seuqence")
    temp_deg = OrderedDict((subj, np.array(nx.degree(graphs[subj]).values()))
                               for subj in graphs)
    deg = density(temp_deg)
    write(outdir, 'degree_distribution', deg, atlas) 

    #  Edge Weights
    print("Computing: Edge Weight Sequence")
    temp_ew = OrderedDict((subj, [graphs[subj].get_edge_data(e[0], e[1])['weight']
                           for e in graphs[subj].edges()]) for subj in graphs)
    ew = density(temp_ew)
    write(outdir, 'edge_weight_distribution', ew, atlas) 

    #   Clustering Coefficients
    print("Computing: Clustering Coefficient Sequence")
    temp_cc = OrderedDict((subj, nx.clustering(graphs[subj]).values())
                           for subj in graphs)
    ccoefs = density(temp_cc)
    write(outdir, 'clustering_coefficients', ccoefs, atlas) 

    # Scan Statistic-1
    print("Computing: Scan Statistic-1 Sequence")
    temp_ss1 = scan_statistic(graphs, 1)
    ss1 = density(temp_ss1)
    write(outdir, 'scan_statistic_1', ss1, atlas) 

    # Eigen Values
    print("Computing: Eigen Value Sequence")
    laplac = OrderedDict((subj, nx.normalized_laplacian_matrix(graphs[subj]))
                             for subj in graphs)
    eigs = OrderedDict((subj, np.sort(np.linalg.eigvals(laplac[subj].A))[::-1])
                                 for subj in graphs)
    write(outdir, 'eigen_sequence', eigs, atlas) 

    # Betweenness Centrality
    print("Computing: Betweenness Centrality Sequence")
    nxbc = nx.algorithms.betweenness_centrality  # For PEP8 line length...
    temp_bc = OrderedDict((subj, nxbc(graphs[subj]).values())
                           for subj in graphs)
    centrality = density(temp_bc)
    write(outdir, 'betweenness_centrality', centrality, atlas) 

    outf = outdir + '/' + atlas + '_summary.png'

    plot_metrics(nnz, deg, ew, ccoefs, ss1, eigs, centrality, outf)


def scan_statistic(mygs, i):
    """
    Computes scan statistic-i on a set of graphs

    Required Parameters:
        mygs:
            - Dictionary of graphs
        i:
            - which scan statistic to compute
    """
    ss = OrderedDict()
    for key in mygs.keys():
        g = mygs[key]
        tmp = np.array(())
        for n in g.nodes():
            sg = nx.ego_graph(g, n, radius=i)
            tmp = np.append(tmp, np.sum([sg.get_edge_data(e[0], e[1])['weight']
                            for e in sg.edges()]))
        ss[key] = tmp
    return ss


def density(data, nbins=1000):
    """
    Computes density for metrics which return vectors

    Required parameters:
        data:
            - Dictionary of the vectors of data
    """
    density = OrderedDict()
    xs = OrderedDict()
    for subj in data:
        dens = gaussian_kde(data[subj])
        xs[subj] = np.linspace(0, 1.2*np.max(data[subj]), nbins)
        density[subj] = dens.evaluate(xs[subj])

    return {"xs": xs, "pdfs": density}


def write(outdir, metric, data, atlas):
    """
    Write computed derivative to disk in a pickle file

    Required parameters:
        outdir:
            - Path to derivative save location
        metric:
            - The value that was calculated
        data:
            - The results of this calculation
        atlas:
            - Name of atlas of interest as it appears in the directory titles
    """
    with open(outdir + '/' + atlas + '_' + metric + '.pkl', 'wb') as of:
        pickle.dump({metric: data}, of)


def main():
    """
    Argument parser and directory crawler. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.

    Required parameters:
        atlas:
            - Name of atlas of interest as it appears in the directory titles
        basepath:
            - Basepath for which data can be found directly inwards from
        outdir:
            - Path to derivative save location
    Optional parameters:
        fmt:
            - Determines file organization; whether graphs are stored as
              .../atlas/dataset/graphs or .../dataset/atlas/graphs. If the
              latter, use the flag.
        verb:
            - Toggles verbose output statements
    """
    parser = ArgumentParser(description="Computes Graph Metrics")
    parser.add_argument("atlas", action="store", help="atlas directory to use")
    parser.add_argument("indir", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    parser.add_argument("-f", "--fmt", action="store_true", help="Formatting \
                        flag. True if bc1, False if greg's laptop.")
    parser.add_argument("-v", "--verb", action="store_true", help="")
    result = parser.parse_args()

    #  Sets up directory to crawl based on the system organization you're
    #  working on. Which organizations are pretty clear by the code, methinks..
    indir = result.indir
    atlas = result.atlas

    #  Crawls directories and creates a dictionary entry of file names for each
    #  dataset which we plan to process.
    fs = [indir + "/" + fl
          for root, dirs, files in os.walk(indir)
          for fl in files
          if fl.endswith(".graphml") or fl.endswith(".gpickle")]

    p = Popen("mkdir -p " + result.outdir, shell=True)
    #  The fun begins and now we load our graphs and process them.
    compute_metrics(fs, result.outdir, atlas, result.verb)


if __name__ == "__main__":
    main()
