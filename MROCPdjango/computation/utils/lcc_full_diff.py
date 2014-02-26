# Author: Disa Mhembere
# Contact: disa@jhu.edu

# A file to write to csv with the difference between the
#  # of edges & vertices of a graph & its LCC
from paths import include
include()

import os
import numpy as np
import scipy.io as sio
import sys
from computation.utils.loadAdjMatrix import loadAdjMat # for loading the LCC

def getDiff(graph_dir, lcc_dir):
  csv = "Sample, Full nodes, LCC nodes, Full edges, LCC edges\n"

  full_vert = []
  full_edge = []
  lcc_vert = []
  lcc_edge = []

  for fn in os.listdir(graph_dir):
    g = sio.loadmat(os.path.join(graph_dir, fn))['fibergraph']
    ##lcc = np.load(os.path.join(lcc_dir, (fn.split('_')[0] + '_concomp.npy')))

    G_lcc = loadAdjMat( os.path.join(graph_dir, fn), os.path.join(lcc_dir, (fn.split('_')[0] + '_concomp.npy')) )
    full_vert.append(g.shape[0])
    full_edge.append(g.nnz)
    lcc_vert.append(G_lcc.shape[0])
    lcc_edge.append(G_lcc.nnz/2)
    print "%s ==> full (n,e)= (%d, %d), lcc (n,e) = (%d, %d)" % (fn, g.shape[0], g.nnz, G_lcc.shape[0], G_lcc.nnz/2) # lcc.view().item().shape[1] , lcc.view().item().nnz)

    csv += "%s, %d, %d, %d, %d\n" % (fn, g.shape[0], G_lcc.shape[0], g.nnz, G_lcc.nnz/2)

  f = open('lcc-full_comp', 'w')
  f.write(csv)
  f.close()

  np.save('full_vert',full_vert)
  np.save('full_edge', full_edge)
  np.save('lcc_vert', lcc_vert)
  np.save('lcc_edge', lcc_edge)

def main():
  if len(sys.argv) > 2:
    getDiff(sys.argv[1], sys.argv[2])
  else:
    print "Please provide command line args 1 and 2"


if __name__ == "__main__":
  main()
