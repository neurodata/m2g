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
from ocpipeline.views import getFiberPath


import scipy.sparse.linalg.eigen.arpack as arpack
from collections import Counter

from time import clock

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
    self.getMaxAveDegree()
    
    ''' Calc scan statistic'''
    print 'Calculating scan statistic 1...'
    self.calcScanStat()
    
    #self.printVertDegrees() # print all degrees
    #self.printVertSS1() # print SS1
    
    ''' Calc scan statistic 2'''
    
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
      
    start = clock()
      # LR = Largest Real part
    self.maxAveDeg = (np.max(arpack.eigs(self.G_sparse, which='LR')[0])).real # get eigenvalues, then +ve max REAL part is MAD eigenvalue estimation
    print "\n Calculating MAD took: ", (clock() - start), "secs"
  
  def getAveDegree(self, vertDegArr):
    '''
    Calculate the Average Degree of a vertex  
    Returns:
    =========
    The Average degree of a vertex
    '''
    return np.average(vertDegreArr)
      
  ####################
  # TODO DM: FIX these #
  ####################
  
  def printVertSS1(self):
    '''
    Print the Scan statistic 1
    '''
    print '\nScan statistics\n=======================\n'
    for idx, vert in enumerate (self.vertices):
      print 'Vertex: %d, Scan stat 1: %d' % (vert.ind, vert.indSubgrEdgeNum)
      
  def printVertDegrees(self):
    '''
    Print the vertex degree of all vertices
    '''
    print '\nVertx Degrees \n=======================\n'
    for idx, vert in enumerate (self.vertices):
      print 'Vertex: %d, Degree 1: %d' % (vert.ind, vert.degree)
  
  
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
  
def calcScanStat(self, G, G_fn='',N=1):
  '''
  G - Sparse adjacency matrix (rep a graph)
  N - Scan statistic number i.e 1 or 2 ONLY
  '''
  if (N == 2):
    G = G.dot(G)+G
  
  vertDeg = np.zeros(G.shape[0]) # Vertex degrees of all vertices
  indSubgrEdgeNum = np.zeros(G.shape[0]) # Induced subgraph edge number i.e scan statistic
  
  for vertx in range (G.shape[0]):
    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex
    nborsAdjMat = G[:,nbors][nbors,:]
    indSubgrEdgeNum[vertx] = nborsAdjMat.nnz # scan stat 1
  
  '''write to file '''
  if not (G_fn):
    np.save(getFiberPath(G_fn) + 'scanstat'+N+'.npy', indSubgrEdgeNum) # save location wrong!
    np.save(getFiberPath(G_fn) + 'degree'+N+'.npy', vertxDeg)  # save location wrong!
  else:
    np.save('scanstat'+N+'.npy', indSubgrEdgeNum)
    np.save('degree'+N+'.npy', vertxDeg)
    
  del vertxDeg, indSubgrEdgeNum

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
  
  if (len(degArray) == len(ss1Array)):
    print "Array lengths unequal"
    sys.exit(-1)
  
  triangles = np.zeros(len(degArray))
  for idx in range (degArray):
    numTri = ss1Array[idx] - degArray[idx]
    if numTri < 0:
      print 'There is an error in index %d. This num cannot be negative' % idx
      
    triangles[idx] = numTri
    
  np.save('triangles.npy', triangles)  # save location wrong!
  
    
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
  gr.loadgraphMatx('/home/disa/testgraphs/M87199728_fiber.mat', True, True, False) # mrbrain
  gr.calcGraphInv()
  
  #import pdb; pdb.set_trace()

if __name__ == '__main__':
  main()

'''

cc(v) = triangle(v)/(degree choose 2)
'''
