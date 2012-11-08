#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Plot all .np arrays in a common dir on the same axis & save
# 1 indexed

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import glob
import argparse

import numpy as np
from scipy import interpolate

def plotInvDist(invDir, toDir, numBins =10):
  
  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)
  
  for arrfn in glob.glob(os.path.join(invDir,'*.npy')):
    try:
      arr = np.load(arrfn)
      #import pdb; pdb.set_trace()
    except:
      print "Ivariant file not found %s"  % arrfn
    plt.figure(1)
    n, bins, patches = plt.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)
  
    n = np.append(n,0)
    plt.figure(2)
    # Flat follow
    plt.plot(bins, n, 'r--', linewidth=1)
    
    # Interpolation
    #f = interpolate.interp1d(bins, n, kind='cubic') 
    
    #x = np.arange(bins[0],bins[-1],0.01) # vary linspc
    #plt.plot(x, f(x),'-b' ,linewidth=1)
    
  plt.title('Invariant distribution')  
  plt.ylabel('Raw count')
  plt.xlabel('Vertex')
  plt.show()
  
  if not os.path.exists(toDir):
    pass #os.makedirs(toDir)
    
  #plt.savefig(os.path.join(toDir, "CombinedEigenvalues.png")) 
  
def main():
    
    parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
    parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .png figure file to go')
    parser.add_argument('numBins', type = int, action='store', help='Number of bins')
    
    result = parser.parse_args()
    plotInvDist(result.invDir, result.toDir, result.numBins)

if __name__ == '__main__':
  main()
  