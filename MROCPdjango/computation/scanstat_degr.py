#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# 10/2/2012
# Calculate the true local scan statistic
import os
import scipy.io as sio
import numpy as np
from math import ceil

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
import argparse

def calcScanStat_Degree(G_fn, lcc_fn = None, roiRootName = None, toDir = None, N=1):
  '''
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  bin - binarize or not
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  N - Scan statistic number i.e 1 or 2 ONLY
  '''
  print '\nCalculating scan statistic %d...' % N
  
  if (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  if (N == 2):
    G = G.dot(G)+G
  
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
    
  vertxDeg = np.zeros(G.shape[0]) # Vertex degrees of all vertices
  indSubgrEdgeNum = np.zeros(G.shape[0]) # Induced subgraph edge number i.e scan statistic

  for vertx in range (G.shape[0]):
    if (vertx > 0 and (vertx% (int(G.shape[0]*0.1)) == 0)):
        print ceil(vertx/(float(G.shape[0]))*100), "% complete..."
   
    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex
    
    if (nbors.shape[0] > 0):
      nborsAdjMat = G[:,nbors][nbors,:]
      indSubgrEdgeNum[vertx] = nbors.shape[0] + nborsAdjMat.nnz # scan stat 1
    else:
      indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph

  print "100 % complete..."
  '''write to file '''
  
  if toDir:
    ss1_fn = os.path.join(toDir, getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    deg_fn = os.path.join(toDir, getBaseName(G_fn) + '_degree.npy')
    
  else: # test
    ss1_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    deg_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_degree.npy')
    
  np.save(ss1_fn, indSubgrEdgeNum) # save location wrong - Should be invariants
  np.save(deg_fn, vertxDeg)  # save location wrong - Should be invariants
    
  del vertxDeg, indSubgrEdgeNum
  return [ss1_fn, deg_fn, G.shape[0]] #return scan stat1, degree of each node, the number of nodes in the graph

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .png figure file to go')
    
    result = parser.parse_args()
    calcScanStat(result.G_fn, result.lcc_fn, result.roiRootName, result.toDir)

if __name__ == '__main__':
  main()
