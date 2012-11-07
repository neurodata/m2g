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

def plotInvDist(invDir, toDir):
  
  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)
  
  for arrfn in glob.glob(os.path.join(invDir,'*')):
      try:
        arr = np.load(arrfn)
      except:
        print "Ivariant file not found %s" % arrfn
      n, bins, patches = plt.hist(arr, bins=10, range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)
      
  plt.title('Invariant distribution')  
  plt.ylabel('y label')
  plt.xlabel('x label')
  plt.show()
  
  if not os.path.exists(toDir):
    pass #os.makedirs(toDir)
    
  #plt.savefig(os.path.join(toDir, "CombinedEigenvalues.png")) 
  
def main():
    
    parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
    parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .png figure file to go')
    
    result = parser.parse_args()
    plotInvDist(result.invDir, result.toDir)

if __name__ == '__main__':
  main()
  