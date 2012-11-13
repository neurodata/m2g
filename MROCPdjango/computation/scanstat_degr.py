#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Calculate the true local scan statistic
import os
import scipy.io as sio
import numpy as np
from math import ceil

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse
from time import time

def calcScanStat_Degree(G_fn, G = None, lcc_fn = None, roiRootName = None, ssDir = None, degDir = None , N=1):
  '''
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  G - the sparse matrix containing the graphs
  bin - binarize or not
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  toDir - Directory where resulting array is placed
  N - Scan statistic number i.e 1 or 2 ONLY
  '''
  print '\nCalculating scan statistic %d...' % N
  
  if (G !=None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  #if (N == 2):
   # G = G.dot(G)+G
  
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
  
  numNodes = G.shape[0]  
  vertxDeg = np.zeros(numNodes) # Vertex degrees of all vertices
  indSubgrEdgeNum = np.zeros(numNodes) # Induced subgraph edge number i.e scan statistic
  
  percNodes = int(numNodes*0.1)
  mulNodes = float(numNodes)

  start = time()
  for vertx in range (numNodes):
    if (vertx > 0 and (vertx% (percNodes) == 0)):
      print ceil((vertx/mulNodes)*100), "% complete..."
   
    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex
    
    if (nbors.shape[0] > 0):
      nborsAdjMat = G[:,nbors][nbors,:]
      
      indSubgrEdgeNum[vertx] = nbors.shape[0] + (nborsAdjMat.nnz/2.0)  # scan stat 1 # Divide by two because of symmetric matrix
    else:
      indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph

  print "100 % complete"
  print "Time taken Scan Stat 1: %f secs" % float(time() - start)
  '''write to file '''
  
  if ssDir:
    ss1_fn = os.path.join(ssDir, getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    deg_fn = os.path.join(degDir, getBaseName(G_fn) + '_degree.npy')
    
  else: # test
    ss1_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    deg_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_degree.npy')
    
  np.save(ss1_fn, indSubgrEdgeNum)
  np.save(deg_fn, vertxDeg)  
  
  del vertxDeg, indSubgrEdgeNum
  return [ss1_fn, deg_fn, G.shape[0]] #return scan stat1, degree of each node, the number of nodes in the graph

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    parser.add_argument('ssDir', action='store', help='Full path of directory where you want Scan stat .npy array resulting file to go')
    parser.add_argument('degDir', action='store', help='Full path of directory where you want Degree .npy array resulting file to go')
    
    ssDir = None, degDir
    result = parser.parse_args()
    
    calcScanStat_Degree(result.G_fn, None, result.lcc_fn, result.roiRootName, result.ssDir, result.degDir)

if __name__ == '__main__':
  main()
