#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Estimation of Weighted local clustering coeffecients
# Based on work by: Jari Saramaki
# Published as: Generalizations of the clustering coefficient to weighted complex networks

import numpy as np
import scipy.special
import numpy as np

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat

import os
import argparse
from time import time

def calcWeightedLocalClustCoeff(G_fn, lcc_fn = None, roiRootName = None, toDir = None, test=False):
  '''
  G_fn - fibergraph full filename (.mat)
  lcc_fn - largest connected component full filename (.npy)
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  test - if true then this is a test else not  
  '''
  
  print "\nCalculating local clustering coeff.."
  start = time()
    
  # Weighted graphs 
  if(weighted):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)  
    
    maxWeight = np.max(G) # max weight of the graph
    maxIdx = G.argmax() #indx of max when flattened
    maxX = maxIdx / G.shape[0] # max x-index
    maxY = maxIdx % G.shape[0]# max y-index
    
    triArr = np.empty_like(degArray)
    
    # (3) Jari et al
    for i in range(G.shape[0]):
      cubedRtSum = 0
      triCnt = 0
      w_i = G.indicies[G.indptr[i]:G.indptr[i+1]]
      for k in range(G.shape[0]):
        w_k = G.indicies[G.indptr[k]:G.indptr[k+1]]
        for j in range(G.shape[0]):
        
          if [j,k] not in w_i:
	    break # No edge
	  if [j] not in w_k:
	    break # No edge
	  
	  iNeigh = G.indices[G.indptr[i]:G.indptr[i+1]]
	  idx_ij = np.where( iNeigh == j)[0][0]
	  idx_ik = np.where( iNeigh == k)[0][0]
	  idx_jk = np.where( G.indices[G.indptr[k]:G.indptr[k+1]] == j)[0][0]
	
	  cubedRtSum += scipy.special.cbrt( (G.data[G.indptr[i]:G.indptr[i+1]][idx_ij])/float(maxWeight) * \
	    (G.data[G.indptr[i]:G.indptr[i+1]][idx_ik])/float(maxWeight) *\
	    (G.data[G.indptr[k]:G.indptr[k+1]][idx_jk])/float(maxWeight) )
	  triCnt += 1
	  
      ccArray[i] = cubedRtSum
      triArr1[i] = triCnt
  
  #ccArray = ccArray*3 # Since cc is concerned with the true number of triangles counted - we include duplicates  
  
  if not test:
    ccArr_fn = os.path.join(toDir, getBaseName(tri_fn) + '_clustcoeff.npy')
    tri_fn = os.path.join(toDir, getBaseName(G_fn) + '_triangles.npy')
  
  else:
    ccArr_fn = os.path.join('bench', str(len(triArray)), getBaseName(tri_fn) + '_clustcoeff.npy')
    tri_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_triangles.npy')
    
  np.save(ccArr_fn, ccArray)  # save location wrong!
  
  print 'Time taken to calc Weighted Clust coeff: %f secs\n' % (time() - start)    
  return ccArr_fn, 

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
    
    result = parser.parse_args()
    calcWeightedLocalClustCoeff(result.G_fn, result.lcc_fn, result.roiRootName, result.toDir)

if __name__ == '__main__':
  main()