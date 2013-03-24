#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Compute all eigenvalues and eigenvectors for a directory

from computation.eigen import calcEigs
from glob import glob
from computation.utils import getBaseName
import os
import argparse


def runEigs(grDir, lccDir, toDir):
  '''
  ********* TEMPORARY FILE *********
  grDir - Full path of dir with graphs
  lccDir - Full path of dir with largest connected components
  '''
  for G_fn in glob(os.path.join(grDir,'*')):
    calcEigs(G_fn, lcc_fn=getLccfn(G_fn), eigvDir = toDir, k=100)
    print G_fn, "Sucessfull processed...\n\n"
  print "****JOB DONE****"

def getLccfn(G_fn):
  '''
  Get the lcc filename form G_fn
  G_fn - full filename of graph (e.g of format /{User}/{disa}/{graphs}/filename_fiber.mat)
  * {} - Not necessary
  '''
  lcc_fn = '/'
  for i in G_fn.split('/')[1:-3]:
    lcc_fn = os.path.join(lcc_fn, i)
  lcc_fn = os.path.join(lcc_fn, "connectedcomp", getBaseName(G_fn)+'_concomp.npy')

  return lcc_fn

def main():

  parser = argparse.ArgumentParser(description='Runs all invariants on all graphs in a Dir')
  parser.add_argument('grDir', action='store',help='Full path of dir with graphs')
  parser.add_argument('lccDir', action='store',help='Full filename of largest connected component Dir')
  parser.add_argument('toDir', action='store', help='Full path of directory where you want .npy array resulting files to go')

  result = parser.parse_args()
  runEigs(result.grDir, result.lccDir, result.toDir)

if __name__ == '__main__':
  main()
