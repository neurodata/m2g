from computation.utils.loadAdjMatrix import loadAdjMat
from glob import glob
import os
import scipy.io as sio
import pdb
import sys

# load up and LCC adjacency matrix and save it elsewhere
def load_and_store(dirg):
  graphs = glob( os.path.join(dirg, "*"))

  if dirg.endswith("//"): dirg = dirg[:-1]
  base_dir = os.path.dirname(os.path.dirname(dirg))
  save_dir = os.path.join(base_dir, "big_lcc_graphs")

  if not os.path.exists(save_dir):
    print "Making %s ..." % save_dir
    os.makedirs(save_dir)

  for g_fn in graphs:
    print "\nProcessing %s ..." % g_fn

    fn_root = g_fn.split("/")[-1][:-13]
    lcc_fn = os.path.join(base_dir, "big_lcc", fn_root+"big_lcc.npy")

    g = loadAdjMat(g_fn, lcc_fn)
    fn = os.path.join(save_dir, fn_root+"big_lcc_adjmat")

    print "Saving %s ..." % fn
    sio.savemat( os.path.join(save_dir, fn), {"data":g} )

  print "Done with %s" % dirg

load_and_store(sys.argv[1])
