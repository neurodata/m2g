#!/usr/bin/python

'''
@author: Disa Mhembere
Determine some graph invariants on big and small graphs
Date: 5 Sept 2012
'''

import scipy.io as sio
import numpy as np
import os
import argparse
import sys

import scipy.sparse.linalg.eigen.arpack as arpack
from collections import Counter

from time import time

class graph():
  def __init__(self):
    '''
    G_sparse - sparse adjacency matrix of graph
    
    size - Number of edges
    classification - This is big or small
    binarize - Whether the graph is binarized or not
    sym - Whether the graph is symmetrized or not
    maxAveDeg - Maximum Average Degree
    vertices - numpy array of vertices 
    '''
    

  def loadgraphMatx(self, graph_fn, big = False, sym = False, binarize = False, toPyMat = False):
    ''' 
    load a graph. symmetrize, binarize & convert to python matrix if specified
    graph_fn - full file name of graph
    sym - symeterrize. Convert from upper triangular to full graph
    binarize - make all non-zero entries 1 else 0
    toPyMat - convert to python list of lists i.e matrix
    '''
    self.G_sparse = sio.loadmat(graph_fn)['fibergraph'] # key is always fibergraph & comp is compressed
    self.binary = binarize
    self.sym = sym
    self.G_fn = graph_fn
    
    if (big):
      self.classification = 'big'
    else:
      self.classification = 'small'
 
 
    self.indices = self.G_sparse.indices
      
    if(self.binary):      
      self.G_sparse.data[:] = 1 # All non-zero entries set to one
            
    if(self.sym):
      self.symmetrize()
      
    self.size = self.G_sparse.getnnz() # Number of edges in graph
      
    if (toPyMat):
      if (big):
	print 'Cannot convert \'big\' matrix to python matrix!'
      else:
	self.G_dense = self.G_sparse.tolist() # turn into python list of lists
  
  #####################
  # SYMMETRIZE MATRIX #
  #####################
  def symmetrize(self):
    '''
    Symmetrize an upper/lower triangular matrix
    '''
    self.G_sparse = self.G_sparse + self.G_sparse.T
    self.sym = True if not (self.sym) else self.sym
  
  ########################
  # RUN GRAPH INVARIANTS #
  ########################
  def calcGraphInv(self):
    '''
    Calculate several graph invariants
    1. The maximum average degree (MAD) of the graph
    2. The degree of each vertex
    3. The Scan Statistic 1
    4. 
    '''
    
    #self.vertices = np.zeros(self.G_sparse.shape[0])
    
    #Create vertex list
    #self.vertices = []
    #for v in range(self.G_sparse.shape[0]):
     # self.vertices.append(vertex(v))
      
    #self.vertices = np.array(self.vertices) # make list a numpy array
    
    ############ Graph Invariant calcs ############
    ''' Calc Maximum Average Degree of the graph'''
    print 'Getting Maximum Average Degree..'
    start = time()
    #self.getMaxAveDegree() # Takes ~5min on 16Mil  vertices with 60Mil edges 
    print 'Time taken to calc MAD: %f secs\n' % (time() - start)

    ''' Calc scan statistic'''
    print 'Calculating scan statistic 1...'
    start = time()
    ss1Array, degArray = calcScanStat(self.G_sparse, G_fn=self.G_fn,N=1)
    print 'Time taken to calc  SS1: %f secs\n' % (time() - start)

    ''' Calc number of triangles'''
    print 'Getting number of triangles...'
    start = time()
    triArray = calcNumTriangles(ss1Array, degArray, G_fn=self.G_fn)
    print 'Time taken to calc Num triangles: %f secs\n' % (time() - start)

    if (self.classification == 'small'):
      printVertInv(ss1Array, 'Scan Statistic 1') # print scan stat 1
      printVertInv(degArray, 'Vertex Degree') # print vertex degree
      printVertInv(triArray, 'Number of triangles') # print number triangles 

  #################################
  # MAX AVERAGE DEGREE EIGENVALUE #
  #################################
    
  def getMaxAveDegree(self):
    '''
    Calc the Eigenvalue Max Average Degree of the graph
    Note this is an estimation and is guaranteed to be greater than or equal to the true MAD
    '''
    if not self.sym:
      self.symmetrize() # Make sure graph is symmetric
      
    start = time()
      # LR = Largest Real part
    self.maxAveDeg = (np.max(arpack.eigs(self.G_sparse, which='LR')[0])).real # get eigenvalues, then +ve max REAL part is MAD eigenvalue estimation
  
  def getAveDegree(self, vertDegArr):
    '''
    Calculate the Average Degree of a vertex  
    Returns:
    =========
    The Average degree of a vertex
    '''
    return np.average(vertDegreArr)
      
  

  def calcNumTriangles(self):
    '''
    Number of traingles in the graph
    '''
    pass
  
  def calcLocalClustCoeff(self):
    '''
    Local clustering coefficient of each vertex
    '''
    pass
  
  def pathLength(self):
    '''
    Path length between each pair of vertices
    '''
    pass

###################
# SCAN STATISTICS #
###################
  
def calcScanStat(G, G_fn='',N=1):
  '''
  G - Sparse adjacency matrix (rep a graph)
  N - Scan statistic number i.e 1 or 2 ONLY
  '''
  if (N == 2):
    G = G.dot(G)+G
  
  vertxDeg = np.zeros(G.shape[0]) # Vertex degrees of all vertices
  indSubgrEdgeNum = np.zeros(G.shape[0]) # Induced subgraph edge number i.e scan statistic
  
  for vertx in range (G.shape[0]):
    if (vertx > 0 and G.classification == 'big' and vertx/G.shape[0]%10 == 0)
	print ((vertx/G.shape[0])*100), "% complete..."
    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex
 
    if (nbors.shape[0] > 0):
      nborsAdjMat = G[:,nbors][nbors,:]
      indSubgrEdgeNum[vertx] = nborsAdjMat.nnz # scan stat 1
    else:
      indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph

  '''write to file '''
  if (G_fn):
    ss1_fn = getbaseName(G_fn) + 'scanstat'+str(N)+'.npy'
    deg_fn = getbaseName(G_fn) + 'degree'+str(N)+'.npy'
    
    np.save(ss1_fn, indSubgrEdgeNum) # save location wrong - Should be invariants
    np.save(deg_fn, vertxDeg)  # save location wrong - Should be invariants
  else:
    np.save('scanstat'+N+'.npy', indSubgrEdgeNum)
    np.save('degree'+N+'.npy', vertxDeg)
    
  # del vertxDeg, indSubgrEdgeNum
  return [ss1_fn, deg_fn]

def calcNumTriangles(ss1Array, degArray, G_fn = ''):
  if not isinstance(ss1Array, np.ndarray):
    try:
      ss1Array = np.load(ss1Array)
    except:
      print "ERROR: File not found: %s OR not valid format" % ss1Array
      sys.exit(-1)
  
  if not isinstance(degArray, np.ndarray):
    try:
      degArray = np.load(degArray)
    except:
      print "File not found: %s" % degArray
      sys.exit(-1)
  
  if (len(degArray) != len(ss1Array)):
    print "Array lengths unequal"
    sys.exit(-1)
  
  triangles = np.subtract(ss1Array, degArray)
  if np.any(triangles[:] < 0):
      print 'No entry should be negative in triangles array!'
      
  if G_fn:
    triArr_fn = getbaseName(G_fn) +'triangles.npy'  
    np.save(triArr_fn, triangles)  # save location wrong!
  else:
    triArr_fn = 'triangles.npy'
    np.save(triArr_fn, triangles)  # save location wrong!
  
  #del triangles
  return triArr_fn 

####################
# Base name getter #
####################
def getbaseName(G_fn):
  return G_fn.partition('_')[0]


######################
# Printing Functions #
######################

def printVertInv(fn, invariantName):
  '''
  fn - Invariant full filename
  invariantName - String describing the invariant 
  Print the Scan statistic 1
  '''
  try:
    inv = np.load(fn)
  except:
    print 'Invalid file name: %s' % fn
    sys.exit(-1)

  print '\n%s\n=======================\n' % (invariantName)
  for idx, vert in enumerate (inv):
    print 'Vertex: %d, Value: %d' % (idx, vert)

##########################
  # Vertex Class #
##########################
class vertex():
  '''
  Class to hold a vertex object
  '''
  def __init__(self, ind ,degree = 0):
    self.degree = degree
    self.adjList = []
    self.ind = ind
    self.indSubgrEdgeNum = 0  # induced subgraph
    

def main():
  gr = graph()
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/Scan/M87102217_smgr.mat', big = False, sym = True, binarize = True)
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/M87199728_fiber.mat', True, True, True)
  #gr.loadgraphMatx('/data/projects/MRN/graphs/biggraphs/M87199728_fiber.mat', True, True, False) # bg1
  #gr.loadgraphMatx('/home/disa/testgraphs/M87102217_smgr.mat', False, True, True) # mrbrain small
  gr.loadgraphMatx('/home/disa/testgraphs/M87199728_fiber.mat', True, True, False) # mrbrain big
  
  gr.calcGraphInv()
  
if __name__ == '__main__':
  main()

'''
cc(v) = triangle(v)/(degree choose 2)
'''
