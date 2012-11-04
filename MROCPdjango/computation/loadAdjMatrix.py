#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Load up an adjacency matrix given G_fn, lcc & roiRoot

import mrpaths
import argparse
import mrcap.lcc as lcc
from getBaseName import getBaseName
import os

def loadAdjMat(G_fn, lcc_fn, roiRootName = None):
  '''
  Load adjacency matrix given lcc_fn & G_fn. lcc has z-indicies corresponding to the lcc :
  G_fn - the .mat file holding graph
  lcc_fn - the largest connected component .npy z-ordering
  '''
  if not roiRootName:
    roiRootName =  os.path.join(getRoiRoot(G_fn),getBaseName(G_fn))
       
  vcc = lcc.ConnectedComponent(fn = lcc_fn)
  try:
    fg = lcc._load_fibergraph(roiRootName , G_fn) 
    G = vcc.induced_subgraph(fg.spcscmat)
    G = G+G.T # Symmetrize
  except:
    print "Problem loading real lcc & graph"
    
  return G

def getRoiRoot(G_fn):
  '''
  Get the roi root name form G_fn
  G_fn - full filename of graph (e.g of format /{User}/{disa}/{graphs}/filename_fiber.mat)
  * {} - Not necessary
  '''
  roiRoot = ''
  for i in G_fn.split('/')[1:-2]:
    roiRoot = os.path.join(roiRoot, i)
  roiRoot = os.path.join(roiRoot, 'roi')
  return roiRoot
  
def main():
    
    parser = argparse.ArgumentParser(description='Calculate Max Avg Degree estimate as max eigenvalue for biggraphs')
    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
    parser.add_argument('roiRootName', action='store',help='Full path of roi director + baseName')
    
    result = parser.parse_args()
    getMaxAveDegree(result.G_fn, result.lcc_fn, result.roiRootName)

if __name__ == '__main__':
  main()
  