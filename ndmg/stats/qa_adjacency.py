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

# qa_adjacency.py
# Created by Vikram Chandrashekhar.
# Email: Greg Kiar @ gkiar@jhu.edu

import os
import networkx as nx
import matplotlib
import numpy as np
from argparse import ArgumentParser

matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt


def graph2png(infile, outdir, fname=None):
    '''
    infile: input .gpickle or .graphml file
    outdir: path to directory to store output png files
    '''
    # if file is .gpickle, otherwise load .graphml
    try:
        graph = nx.read_gpickle(infile)
    except:
        graph = nx.read_graphml(infile)
    # get numpy array equivalent of adjacency matrix
    g = nx.adj_matrix(graph).todense()
    fig = plt.figure(figsize=(7, 7))
    # plot adjacency matrix
    p = plt.imshow(g, interpolation='None', cmap='jet')
    if fname is None:
        fname = os.path.split(infile)[1].split('.')[0] + '.png'
    save_location = outdir + fname
    plt.savefig(save_location, format='png')
    print(fname + ' done!')


def main():
    """
    Argument parser and directory crawler. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.
    Required parameters:
        infile:
            - Basepath for which data can be found directly inwards from
        outdir:
            - Path to derivative save location
    """
    parser = ArgumentParser(description="Generates a visual representation of"
                            " adjacency matrix")
    parser.add_argument("infile", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="save output file"
                        " location")
    result = parser.parse_args()

    if (not os.path.isdir(result.outdir)):
        os.mkdir(result.outdir)
    graph2png(result.infile, result.outdir)

if __name__ == "__main__":
    main()
