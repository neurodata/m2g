#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Calculate the local vertex degree
import os
import scipy.io as sio
import numpy as np
from math import ceil

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time

def calcDegree(G_fn, G = None, lcc_fn = None, degDir = None):
  '''
  Count the degree of each vertex of a graph
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graphs
  lcc_fn - largest connected component full filename (.npy)
  degDir - Directory where resulting degree array is placed
  '''
  print '\nCalculating vertex degree ...'

  if (G !=None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn)

  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']

  numNodes = G.shape[0]
  vertxDeg = np.zeros(numNodes) # Vertex degrees of all vertices

  percNodes = int(numNodes*0.1)
  mulNodes = float(numNodes)

  start = time()
  for vertx in range (numNodes):
    if (vertx > 0 and (vertx% (percNodes) == 0)):
      print ceil((vertx/mulNodes)*100), "% complete..."

    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex

  print "100 % complete"
  print "Time taken vertex degree: %f secs" % float(time() - start)
  '''write to file '''

  if degDir:
    deg_fn = os.path.join(degDir, getBaseName(G_fn) + '_degree.npy')

  else: # test
    deg_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_degree.npy')

  np.save(deg_fn, vertxDeg)

  del vertxDeg
  return deg_fn #return the degree of each node

def main():

    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('degDir', action='store', help='Full path of directory where you want Degree .npy array resulting file to go')

    result = parser.parse_args()

    calcScanStat_Degree(result.G_fn, None, result.lcc_fn, result.degDir)

if __name__ == '__main__':
  main()
