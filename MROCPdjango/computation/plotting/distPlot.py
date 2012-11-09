#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Plot all .np arrays in a common dir on the same axis & save
# 1 indexed

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pylab as pl

import numpy as np
import os
import sys
import glob
import argparse

from scipy import interpolate


def plotInvDist(invDir, pngName, numBins =100):
  # ClustCoeff  Degree  Eigen  MAD  numEdges.npy  ScanStat  Triangle
  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen"
  SS1dir = "ScanStat"
  triDir = "Triangle"
  
  invDirs = [MADdir, ccDir, DegDir, EigDir, SS1dir, triDir]
  
  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)
  
  # for idx, drty in enumerate (invDirs):
  # for arrfn in glob.glob(os.path.join(invDir, drty,'*.npy')):
    
  for arrfn in glob.glob(os.path.join(invDir,'*.npy')):
    try:
      arr = np.load(arrfn)
      import pdb; pdb.set_trace()
      arr = np.log(arr[arr.nonzero()])
      print "Processing %s..." % arrfn
    except:
      print "Ivariant file not found %s"  % arrfn
    pl.figure(1)
    n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)
    n = n/float(sum(n))
    
    pl.figure(2)
    # Flat follow
    #pl.plot(bins, n, '-r', linewidth=1)
    
    # Interpolation
    f = interpolate.interp1d(bins, n, kind='cubic') 
    
    x = np.arange(bins[0],bins[-1],0.03) # vary linspc
    
    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0
    pl.plot(x, interp,color ='grey' ,linewidth=1)
    
  #pl.title('Triangle Count')  
  #pl.title('Scan1')  
  #pl.title('Clustering Co-eff')  
  pl.ylabel('Raw bin count')
  pl.xlabel('log count')
  
  #pl.show()
  
  #if not os.path.exists(toDir):
  #  os.makedirs(toDir)
    
  pl.savefig(pngName) 
  #pl.savefig(os.path.join(toDir, "CombinedTriangles.png")) 
  
def main():
    
    parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
    parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
    parser.add_argument('pngName', action='store', help='Full path of directory of resulting png file')
    parser.add_argument('numBins', type = int, action='store', help='Number of bins')
    
    result = parser.parse_args()
    
    plotInvDist(result.invDir, result.pngName, result.numBins)

if __name__ == '__main__':
  main()
  
