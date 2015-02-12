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

# graphmltomat.py
# Created by Greg Kiar on 2015-02-04.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from argparse import ArgumentParser
import os
from re import findall
from scipy.sparse import lil_matrix, triu
from scipy.io import savemat


def graphconvert(ingraph, outgraph):
  inf = open(ingraph, 'r')
  edges = []
  weight = []
  for line in inf:
    edges += findall('<edge source="n(\d+)" target="n(\d+)">', line)
    weight += findall('<data key="e_weight">(\d+)</data>', line)

  graph = lil_matrix((70,70))
  for i in range(len(weight)):
    idx1 = int(edges[i][0])-1
    idx2 = int(edges[i][1])-1

    graph[idx1, idx2]=int(weight[i])
    graph[idx2, idx1]=int(weight[i])
  
  graph = triu(graph)
  mdict = {"graph": graph}
  savemat(outgraph, mdict)
  
def main():
  parser = ArgumentParser(description="")
  parser.add_argument("ingraph", action="store", help="input graph in graphml format")
  parser.add_argument("outgraph", action="store", help="output graph in mat format")
 
  result = parser.parse_args()
  
  graphconvert(result.ingraph, result.outgraph)

if __name__=='__main__':
  main()
