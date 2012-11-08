#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Plot all .np arrays in a common dir on the same axis & save
# 1 indexed

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from glob import glob

def plotEigs(eigValDir, toDir):
  
  if not os.path.exists(eigValDir):
    print "%s does not exist" % eigValDir
    sys.exit(1)
  
  n = 0
  for eigValInstance in glob(os.path.join(eigValDir,"*.npy")):
    try:
      eigv = np.load(eigValInstance)
    except:
      print "Eigenvalue array"
    
    #if n == 0:
    n = len(eigv)
    plt.plot([range(1,n+1)], eigv,'-b')
    #plt.axis([1, n+1]) # DM TODO: Axis scaling 
      
  plt.title('Top 50 largest eigenvalues')  
  plt.ylabel('Eigenvalue number')
  plt.xlabel('Eigenvalue')
  plt.show()
  
  if not  os.path.exists():
    os.makedirs(toDir)
    
  plt.savefig(os.path.join(toDir, "CombinedEigenvalues.png")) 
  
def main():
    
    parser = argparse.ArgumentParser(description='Plot top 50 eigenvalues for biggraphs')
    parser.add_argument('eigValDir', action='store',help='The full path of directory containing .npy eigenvalue arrays')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want .png figure file to go')
    
    result = parser.parse_args()
    plotEigs(result.eigValDir, result.toDir)

if __name__ == '__main__':
  main()
  