#!/usr/bin/env python
# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

# graphml2mat.py
# Created by Greg Kiar on 2015-04-29.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

"""
Converts graphml format graphs to mat format.
This utility can be applied to graphs of /any/ size in graphml format that you wish to transform to a mat file format. Note that this currently does not preserve edge or node atrributes, and assumes an undirected but weighted graph. You have the option to delete isolates or leave them untouched, as well.

  Inputs
      graph: a graphml formatted graph (equivalent to those produced from the igraph library)
			prune (optional): argument to delete zero degree nodes
  Returns
      graph: a mat formatted graph in the form of an NxN adjacency matrix, where N is the number of nodes in the original graph.
"""

from argparse import ArgumentParser
from scipy.sparse import lil_matrix, triu
from scipy.io import savemat
from igraph import Graph
from copy import copy

def graphml2mat(ingraph, outgraph, prune=False):
	ing = Graph.Read_GraphML(ingraph)
	
	if prune:
		#delete zero degree nodes
		#GK TODO: be smarter
		i = list()
		for n, v in enumerate(ing.vs):
			if v.degree() == 0:
				i.append(n)
		ing.vs[i].delete()
	
	outg = lil_matrix((ing.vcount(), ing.vcount()))

	for e in ing.es:
		outg[e.source, e.target] = e['weight']
		outg[e.target, e.source] = e['weight'] #since edges are undirected add both ways

	outg = triu(outg)
	mat_dict = {"graph": outg}
	savemat(outgraph, mat_dict)


def main():
	parser = ArgumentParser(description="")
	parser.add_argument("ingraph", action="store", help="input graph in graphml format")
	parser.add_argument("outgraph", action="store", help="output graph in mat format")
	parser.add_argument("--prune", "-p", action="store", help="if you want to delete zero degree nodes", default=False, type=bool)
	result = parser.parse_args()

	graphml2mat(result.ingraph, result.outgraph, result.prune)

if __name__=='__main__':
	main()
