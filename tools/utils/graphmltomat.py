#!/usr/bin/env python

from argparse import ArgumentParser
import os
from re import findall
from scipy.sparse import lil_matrix
from scipy.io import savemat


def graphconvert(ingraph, outgraph):
  inf = open(ingraph, 'r')
  edges = []
  weight = []
  for line in inf:
    print line
    edges += findall('<edge source="n(\d+)" target="n(\d+)">', line)
    weight += findall('<data key="e_weight">(\d+)</data>', line)

  graph = lil_matrix((70,70))
  for i in range(len(weight)):
    idx1 = int(edges[i][0])-1
    idx2 = int(edges[i][1])-1
    if idx1 > 35:
      idx1 -= 65
    if idx2 > 35:
      idx2 -= 65
    graph[idx1, idx2]=int(weight[i])
  
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