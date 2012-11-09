#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Plot all .np arrays in a common dir on the same axis & save
# 1 indexed

import matplotlib
matplotlib.use("Agg")

import pylab as pl
#import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from glob import glob
import argparse

def plotEigs(eigValDir, toDir):
  
  if not os.path.exists(eigValDir):
    print "%s does not exist" % eigValDir
    sys.exit(1)
  
  for eigValInstance in glob(os.path.join(eigValDir,"*.npy")):
    try:
      eigv = np.load(eigValInstance)
    except:
      print "Eigenvalue array"
    
    n = len(eigv)
    #import pdb; pdb.set_trace()
    pl.plot(range(1,n+1), np.sort(eigv),'o', color='grey')
    #plt.axis([1, n+1]) # DM TODO: Axis scaling 
   
  pl.title('Clustering Coefficient')
  pl.xlabel('log count')
  pl.ylabel('Raw bin count')   
  #pl.title('Sorted edges per graph')  
  #pl.ylabel('Edges Count')
  #pl.xlabel('Graph Number')
  #pl.ylabel('Eigenvalue')
  #pl.xlabel('Rank')
  pl.show()
  
  #if not os.path.exists():
  #  os.makedirs(toDir)
    
  pl.savefig(os.path.join(toDir, "edgenum.png")) 
  #pl.savefig(os.path.join(toDir, "eigs.png")) 
  
def main():
    
    parser = argparse.ArgumentParser(description='Plot top 50 eigenvalues for biggraphs')
    parser.add_argument('eigValDir', action='store',help='The full path of directory containing .npy eigenvalue arrays')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .png figure file to go')
    
    result = parser.parse_args()
    plotEigs(result.eigValDir, result.toDir)

if __name__ == '__main__':
  main()
  
