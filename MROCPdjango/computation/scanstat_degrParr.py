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

import pp

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

  cpu1 = range(numNodes/4)
  cpu2 = range(cpu1[-1]+1,cpu1[-1]+(numNodes/4))
  cpu3 = range(cpu2[-1]+1,cpu2[-1]+(numNodes/4))
  cpu4 = range(cpu3[-1]+1, numNodes)
  
  ppservers = ()
  job_server = pp.Server(ppservers=ppservers)
  import pdb; pdb.set_trace() 
  
  job_server = pp.Server()
  job_server.set_ncpus(4) 
  start = time()

  j1 = job_server.submit(popSSarray, (cpu1,G,1) , (),("numpy","scipy","math",))
  j2 = job_server.submit(popSSarray, (cpu2,G,2), (),("numpy","scipy","math",)) 
  j3 = job_server.submit(popSSarray, (cpu3,G,3), (),("numpy","scipy","math",))
  j4 = job_server.submit(popSSarray, (cpu4,G,4), (),("numpy","scipy","math",)) 
  #import pdb; pdb.set_trace() 
  job_server.wait()
  indSubgrEdgeNum[cpu1[0]:cpu1[-1]], vertxDeg[cpu1[0]:cpu1[-1]] = j1()
  indSubgrEdgeNum[cpu2[0]:cpu2[-1]], vertxDeg[cpu2[0]:cpu2[-1]] = j2()
  indSubgrEdgeNum[cpu3[0]:cpu3[-1]], vertxDeg[cpu3[0]:cpu3[-1]] = j3()
  indSubgrEdgeNum[cpu4[0]:cpu4[-1]], vertxDeg[cpu4[0]:cpu4[-1]] = j4()

  #j1 = popSSarray(cpu1,G,1);
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

def popSSarray(rangeNodes, G, processorNum):
  #import numpy
  #from math import ceil
  print "Process %d start..." % processorNum
  percNodes = int(len(rangeNodes)*0.1)
  mulNodes = float(len(rangeNodes))

  indSubgrEdgeNum = numpy.zeros(len(rangeNodes))
  vertxDeg = numpy.zeros(len(rangeNodes))

  for vertx in rangeNodes:
    if (vertx > 0 and (vertx% (percNodes) == 0)):
      print "Processor %d: %.1f%% complete..." % (processorNum ,math.ceil((vertx/mulNodes)*100))

    nbors = G[:,vertx].nonzero()[0] 
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex 
    
    if (nbors.shape[0] > 0):
      nborsAdjMat = G[:,nbors][nbors,:]
      
      indSubgrEdgeNum[vertx] = nbors.shape[0] + (nborsAdjMat.nnz/2.0)  # scan stat 1 # Divide by two because of symmetric matrix
    else:
      indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph
  return indSubgrEdgeNum
  print "Processor %d 100%% complete" % processorNum

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    parser.add_argument('ssDir', action='store', help='Full path of directory where you want Scan stat .npy array resulting file to go')
    parser.add_argument('degDir', action='store', help='Full path of directory where you want Degree .npy array resulting file to go')
    
    result = parser.parse_args()
    
    calcScanStat_Degree(result.G_fn, None, result.lcc_fn, result.roiRootName, result.ssDir, result.degDir)

if __name__ == '__main__':
  main()
