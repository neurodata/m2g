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

# loadGraphs.py
# Created by Greg Kiar on 2016-05-11.
# Email: gkiar@jhu.edu
# Edited by Eric Bridgeford.


import warnings

warnings.simplefilter("ignore")
from collections import OrderedDict
import numpy as np
import networkx as nx
import os
import csv


def loadGraphs(filenames, modality="dwi", verb=False):
    """
    Given a list of files, returns a dictionary of graphs
    Required parameters:
        filenames:
            - List of filenames for graphs
    Optional parameters:
        verb:
            - Toggles verbose output statements
    """
    #  Initializes empty dictionary
    if type(filenames) is not list:
        filenames = [filenames]
    gstruct = OrderedDict()
    vlist = set()
    for idx, files in enumerate(filenames):
        if verb:
            print("Loading: " + files)
        #  Adds graphs to dictionary with key being filename
        fname = os.path.basename(files)
        try:
            gstruct[fname] = loadGraph(files, modality=modality)
            vlist |= set(gstruct[fname].nodes())
        except:
            print("{} is not in proper format. Skipping...".format(fname))
    for k, v in list(gstruct.items()):
        vtx_to_add = list(np.setdiff1d(list(vlist), list(v.nodes())))
        [gstruct[k].add_node(vtx) for vtx in vtx_to_add]
    return gstruct


def loadGraph(filename, modality="dwi", verb=False):
    if modality == "dwi":
        graph = nx.read_weighted_edgelist(filename, delimiter=",")
    elif modality == "func":
        # read first line to int list
        with open(filename, "r") as fl:
            reader = csv.reader(fl)
            # labels
            labs = [int(x) for x in next(reader)]
        # read second line onwards to numpy array
        data = np.genfromtxt(filename, dtype=float, delimiter=",", skip_header=True)
        lab_map = dict(list(zip(list(range(0, len(labs))), labs)))
        graph = nx.from_numpy_matrix(data)
        graph = nx.relabel_nodes(graph, lab_map)
    else:
        raise ValueError("Unsupported modality.")
    return graph
