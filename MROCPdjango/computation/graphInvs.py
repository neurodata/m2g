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
    2. 
    '''
    self.vertices = np.zeros(self.G_sparse.shape[0])
    
    # Create vertex list
    self.vertices = []
    for v in range(self.G_sparse.shape[0]):
      self.vertices.append(vertex(v))
      
    self.vertices = np.array(self.vertices) # make list a numpy array
    
    ############ Graph Invariant calcs ############
    ''' Calc Maximum Average Degree of the graph'''
    print 'Getting Maximum Average Degree..'
    self.getMaxAveDegree()
    
    ''' Calc scan statistic'''
    print 'Calculating scan statistic 1...'
    self.calcScanStat()
    
    self.printVertDegrees() # print all degrees
    self.printVertSS1() # print SS1
    
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
  
  ####################
  # INDUCED SUBGRAPH #
  ####################
  def calcScanStat(self, N=1):
    '''
    Determine scan statistic of neighborhood n = N
    '''  
    for vertx in self.vertices: 
    
      # Count edges
      col = vertx.ind; # index corresponds to vertex number
      vertx.indSubgrEdgeNum = self.G_sparse.indptr[col+1] - self.G_sparse.indptr[col] # wheel vertex edges
      
      #import pdb; pdb.set_trace()
      # This happens to also be the vertex degree
      vertx.degree = self.G_sparse.indptr[col+1] - self.G_sparse.indptr[col] # wheel vertex edges
      
      adj = self.G_sparse.indices[self.G_sparse.indptr[col]:self.G_sparse.indptr[col+1]] # Rows of nnz entries - corresponding to vertices
      '''
      Count the list of all matches
      Going to adj[idx:] ensures no double counting
      '''
      for idx, v in enumerate (adj):
	vertx.indSubgrEdgeNum += len(list( (Counter(self.G_sparse.indices[self.G_sparse.indptr[v]:\
					    self.G_sparse.indptr[v+1]]) & Counter(adj[idx:])).elements()))

      # Write all edge numbers to file then del
      
	
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
    
  # Unused currently
  def getAveDegree(self):
    '''
    Calculate the Average Degree of a vertex
    
    Returns:
    =========
    The Average degree of a vertex
    '''
    order = self.degree + 1 # Order of induced sub-graph of vertex i.e vertex cardinality
    
    if (self.indSubgrSize > 0):
      self.aveDeg = (2*self.indSubgrSize)/self.order # Average Degree of graph eq.2.3 p.4
    # else it remains zero
    return self.aveDeg

##########################
  # Edge Class #
##########################

class edge():
  
  def __init__(self):
    pass


def main():
  gr = graph()
  gr.loadgraphMatx('/Users/dmhembere44/Downloads/Scan/M87102217_smgr.mat', big = False, sym = True, binarize = True)
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/M87199728_fiber.mat', True, True, True)
  #gr.loadgraphMatx('/data/projects/MRN/graphs/biggraphs/M87199728_fiber.mat', True, True, False) # server
  gr.calcGraphInv()
  
  #import pdb; pdb.set_trace()

if __name__ == '__main__':
  main()
'''
neigh = G [:,v].nonzero()[0]
An = G[:,neigh][neigh,:]
s1 =  An.sum()

G2 = G.dot(G)+G

Forget scan 2

triange(v) = scan1 - degree
cc(v) = triangle(v)/(degree choose 2)
'''
