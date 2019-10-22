#!/usr/bin/env python

"""
ndmg.utils.loadGraphs
~~~~~~~~~~~~~~~~~~~~~

Contains functionality for working with groups of graph outputs.
TODO : likely largely depracate and replace with `graphutils`.
"""


import warnings

warnings.simplefilter("ignore")
from collections import OrderedDict
import numpy as np
import networkx as nx
import os
import csv


def loadGraphs(filenames, modality="dwi", verb=False):
    """Given a list of files, returns a dictionary of graphs
    
    Parameters
    ----------
    filenames : list
        List of filenames for graphs
    modality : str, optional
        image type of files being loaded, by default "dwi"
    verb : bool, optional
        Toggles verbose output statements, by default False
    
    Returns
    -------
    dict
        dictonary of graphs specified in 'filenames'
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
    """Given a graph file, returns a NetworkX graph
    
    Parameters
    ----------
    filename : str
        Path to graph file to be read by networkx.read_weighted_edgelist
    modality : str, optional
        image type of file being loaded, by default "dwi"
    verb : bool, optional
        Toggles verbose output statements, by default False
    
    Returns
    -------
    graph
        NetworkX graph
    
    Raises
    ------
    ValueError
        Unsupported modality
    """
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
