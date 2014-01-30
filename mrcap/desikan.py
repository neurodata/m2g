#!/usr/bin/python

# desikan.py
# Created by Disa Mhembere on 2014-01-08.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# Mapping of Desikan regions. *Note: 0-based
des_map = {
0:"lh-unknown", 1:"lh-bankssts", 2:"lh-caudalanteriorcingulate",
3:"lh-caudalmiddlefrontal", 4:"lh-corpuscallosum", 5:"lh-cuneus",
6:"lh-entorhinal", 7:"lh-fusiform", 8:"lh-inferiorparietal",
9:"lh-inferiortemporal", 10:"lh-isthmuscingulate", 11:"lh-lateraloccipital",
12:"lh-lateralorbitofrontal", 13:"lh-lingual", 14:"lh-medialorbitofrontal",
15:"lh-middletemporal", 16:"lh-parahippocampal", 17:"lh-paracentral",
18:"lh-parsopercularis", 19:"lh-parsorbitalis", 20:"lh-parstriangularis",
21:"lh-pericalcarine", 22:"lh-postcentral", 23:"lh-posteriorcingulate",
24:"lh-precentral", 25:"lh-precuneus", 26:"lh-rostralanteriorcingulate",
27:"lh-rostralmiddlefrontal", 28:"lh-superiorfrontal", 29:"lh-superiorparietal",
30:"lh-superiortemporal", 31:"lh-supramarginal", 32:"lh-frontalpole",
33:"lh-temporalpole", 34:"lh-transversetemporal",

35:"rh-unknown", 36:"rh-bankssts", 37:"rh-caudalanteriorcingulate",
38:"rh-caudalmiddlefrontal", 39:"rh-corpuscallosum", 40:"rh-cuneus",
41:"rh-entorhinal", 42:"rh-fusiform", 43:"rh-inferiorparietal",
44:"rh-inferiortemporal", 45:"rh-isthmuscingulate", 46:"rh-lateraloccipital",
47:"rh-lateralorbitofrontal", 48:"rh-lingual", 49:"rh-medialorbitofrontal",
50:"rh-middletemporal", 51:"rh-parahippocampal", 52:"rh-paracentral",
53:"rh-parsopercularis", 54:"rh-parsorbitalis", 55:"rh-parstriangularis",
56:"rh-pericalcarine", 57:"rh-postcentral", 58:"rh-posteriorcingulate",
59:"rh-precentral", 60:"rh-precuneus", 61:"rh-rostralanteriorcingulate",
62:"rh-rostralmiddlefrontal", 63:"rh-superiorfrontal", 64:"rh-superiorparietal",
65:"rh-superiortemporal", 66:"rh-supramarginal", 67:"rh-frontalpole",
68:"rh-temporalpole", 69:"rh-transversetemporal"
}

# Note following for desikan labels
# [0-34] -> [0-34] # left hemisphere
# [101-135] -> [35 - 69] # right hemisphere

from zindex import MortonXYZ
import scipy.io as sio

class DesMap():
  def __init__(self, label_fn):
    self.labels = sio.loadmat(label_fn)["labels"]

  def get_mapping(self, vertex):
    x,y,z = MortonXYZ(vertex)
    des_val = self.labels[x, y, z]
    if des_val > 100: des_val -= 66
    return ( des_map[des_val] )

  def get_all_mappings(self, vertices):
    regions = []
    for vertex in vertices:
      regions.append(self.get_mapping(vertex))
    return regions