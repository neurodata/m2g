import scipy.io as sio
from glob import glob
import os
import numpy as np
import argparse
import loadAdjMatrix
from getBaseName import getBaseName

def main():

  parser = argparse.ArgumentParser(description='Get GLOBAL number of edges and vertices for directory of graphs')
  parser.add_argument('grDir', action='store',help='Full filename sparse graph (.mat) directory')
  parser.add_argument('saveDir', action='store', help='Full path of directory where you want .npy array resulting files to go')

  result = parser.parse_args()
  #countVerticesAndEdges(result.grDir, result.saveDir)
  countLCCVerticesAndEdges(result.grDir, result.saveDir)


def root(arrfn):
  return (arrfn.split('/')[-1]).split('_')[0]

def countVerticesAndEdges(grDir, saveDir):

  numVertDict = {}
  numEdgesDict = {}

  numVertLCCDict = {}
  numVertLCCDict = {}

  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
    print 'Directory created --> %s'

  for f in glob(os.path.join(grDir,"*")):
    print "Processing", f
    G = sio.loadmat(f)['fibergraph']
    numVertDict[root(f)] = G.shape[0]

    edgeCount = 0 # Individual count of edge per graph
    for vertex in range(G.shape[0]):
      edgeCount += G[vertex].nnz
    numEdgesDict[root(f)] = edgeCount

  np.save(os.path.join(saveDir, 'numVerticesDict'), np.array(numVertDict)) # save the number of vertices
  np.save(os.path.join(saveDir, 'numEdgesDict'), np.array(numEdgesDict)) # save the number of edges


def countLCCVerticesAndEdges(grDir, saveDir):

  numVertLCCDict = {}
  numEdgeLCCDict = {}

  if not os.path.exists(saveDir):
    os.makedirs(saveDir)
    print 'Directory created --> %s'

  for f in glob(os.path.join(grDir,"*")):
    print "Processing %s .." % f
    G = loadAdjMat(f,'/data/projects/MR/MRN/connectedcomp/'+ getBaseName(f) + '_concomp.npy')
    numVertDict[root(f)] = G.shape[0]

    #edgeCount = 0 # Individual count of edge per graph
    #for vertex in range(G.shape[0]):
    #  edgeCount += G[vertex].nnz
    #numEdgesDict[root(f)] = edgeCount

  np.save(os.path.join(saveDir, 'numLCCVerticesDict'), np.array(numVertLCCDict)) # save the number of vertices
  #np.save(os.path.join(saveDir, 'numEdgesDict'), np.array(numEdgesDict)) # save the number of edges

if __name__ == '__main__':
  main()
