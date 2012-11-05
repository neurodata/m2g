#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Estimation of local clustering coeffecients
# Based on work by: Jari Saramaki
# Published as: Generalizations of the clustering coefficient to weighted complex networks

import numpy as np

from getBaseName import getBaseName

import os
import argparse
from time import time

def calcLocalClustCoeff(deg_fn, tri_fn, degArray = None, triArray = None, ccDir=None, test=False):
  '''
  deg_fn  full filename of file containing an numpy array with vertex degrees
  tri_fn - full filename of file containing an numpy array with num triangles
  degArray - Numpy array holding local degree
  triArray - Numpy array holding local triangle count
  ccDir - Directory where resulting array is placed
  test - if true then this is a test else not
  '''
  
  print "\nCalculating local clustering coeff.."
  
  if (degArray and triArray):
    pass
  
  else:
    degArray = np.load(deg_fn)
    triArray = np.load(tri_fn)
    
  ccArray = np.empty_like(degArray)
  
  if len(degArray) != len(triArray):
    print "Lengths of triangle and degree arrays must be equal"
    sys.exit(-1)
  
  start = time()
  
  for u in range (len(degArray)):
    if (degArray[u] > 2):
      ccArray[u] = (2.0 * triArray[u]) / ( degArray[u] * (degArray[u] - 1) ) #(1) Jari et al
    else:
      ccArray[u] = 0
  
  ccArray = ccArray*3 # Since cc is concerned with the true number of triangles counted - we include duplicates  
  
  if not test:
    ccArr_fn = os.path.join(ccDir, getBaseName(tri_fn) + '_clustcoeff.npy')
  else:
    ccArr_fn = os.path.join('bench', str(len(triArray)), getBaseName(tri_fn) + '_clustcoeff.npy')
  
  np.save(ccArr_fn, ccArray)
  
  print 'Time taken to calc clustering co-efficient: %f secs\n' % (time() - start)    
  return ccArr_fn

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('deg_fn', action='store',help='Full filename of (.npy) file containing the degree per vertex')
    parser.add_argument('tri_fn', action='store',help='Full filename of triangle count array (.npy)')
    parser.add_argument('ccDir', action='store', help='Full path of directory where you want .npy array resulting file to go')
    parser.add_argument('-t','--test', action='store',help='Test if true')
    
    result = parser.parse_args()
    
    if (result.test):
      calcLocalClustCoeff(result.deg_fn, result.tri_fn, None, None, result.ccDir, test=True)
    else:
      calcLocalClustCoeff(result.deg_fn, result.tri_fn, None, None, result.ccDir, test=False)

if __name__ == '__main__':
  main()