from paths import include
include()

from computation.utils.loadAdjMatrix import loadAdjMat
from glob import glob
import os
import scipy.io as sio
import pdb
import sys

def load_and_store(dirg):
  """"
  load up and LCC adjacency matrix and save it elsewhere

  *NOTE: This is not a general script and is specific to the bg1:/data/public/MR/MIGRAINE data
  Positional Args:
  ===============
  dirg - the directory with a graph
  """
  print "** Processing dataset: %s ... **\n" % dirg

  graphs = glob( os.path.join(dirg, "*"))

  if dirg.endswith("//"): dirg = dirg[:-1]
  base_dir = os.path.dirname(dirg)
  save_dir = os.path.join(base_dir, "big_lcc_graphs")

  if not os.path.exists(save_dir):
    print "Making %s ..." % save_dir
    os.makedirs(save_dir)

  for g_fn in graphs:
    print "\nProcessing %s ..." % g_fn

    fn_root = g_fn.split("/")[-1][:-13]
    lcc_fn = os.path.join(base_dir, "big_lcc", fn_root+"big_lcc.npy")

    if os.path.exists(g_fn) and os.path.exists(lcc_fn):
      g = loadAdjMat(g_fn, lcc_fn)
      fn = os.path.join(save_dir, fn_root+"big_lcc_adjmat")
      print "Saving %s ..." % fn
      sio.savemat( os.path.join(save_dir, fn), {"data":g} )

    else:
      if not os.path.exists(g_fn): print "Graph path %s does not exist ..." % g_fn
      if not os.path.exists(lcc_fn): print "Lcc path %s does not exist ..." % lcc_fn

  print "** Done with %s ** \n\n" % dirg

if __name__ == '__main__':
  if len(sys.argv) > 1:
    load_and_store(sys.argv[1])
  else:
    print "Please provide the name of the directory with LCC's to convert as the first arg!"
