import scipy.io as sio
from glob import glob
import os
import numpy as np
import argparse

def main():

  parser = argparse.ArgumentParser(description='Get GLOBAL number of edges and vertices for directory of graphs')
  parser.add_argument('grDir', action='store',help='Full filename sparse graph (.mat) directory')
  parser.add_argument('saveDir', action='store', help='Full path of directory where you want .npy array resulting files to go')

  result = parser.parse_args()
  countVerticesAndEdges(result.G_fn, result.saveDir)

def countVerticesAndEdges(grDir, saveDir):
  numvertices = []
  numEdges = []

  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
    print 'Directory created --> %s'

  for f in glob(os.path.join(grDir,"*")):
    G = sio.loadmat(f)['fibergraph']
    numvertices.append(G.shape[0]) # gets global num edges

    edgeCount = 0 # Individual count of edge per graph
    for vertex in  G.shape[0]:
      edgeCount += G[0].nnz
    numEdges.append(edgeCount)

    import pdb; pdb.set_trace()

  np.save(os.path.join(saveDir, 'numVerices'), np.array(numvertices)) # save the number of vertices
  np.save(os.path.join(saveDir, 'numEdges'), np.array(numEdges)) # save the number of edges

if __name__ == '__main__':
  main()