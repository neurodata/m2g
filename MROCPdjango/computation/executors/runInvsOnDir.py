from genTrueInvs import realgraph
from computation.utils import getBaseName

import os
import argparse
import glob
from math import ceil

def runInvariants(grDir, lccDir, toDir, start, stop):
  '''
  grDir - Full path of dir with graphs
  lccDir - Full path of dir with largest connected components
  '''

  files = glob.glob(os.path.join(grDir,'*'))
  for n, G_fn in enumerate (files[start:stop]):
    realgraph(G_fn, getLccfn(G_fn), toDir)
    print "\n\n*Sucessfull Invariants run*\n\n"

def getLccfn(G_fn):
  '''
  Get the lcc file name form G_fn
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
  parser.add_argument('start', type = int, action='store', help='start pos') # too tired
  parser.add_argument('stop', type = int, action='store', help='stop pos') # too tired

  result = parser.parse_args()

  runInvariants(result.grDir, result.lccDir, result.toDir, result.start, result.stop)

if __name__ == '__main__':
  main()
