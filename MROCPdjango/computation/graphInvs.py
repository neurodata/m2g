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
  
  ##### ******************** #####
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
    
    
    #''' Get the degree of each vertex in the graph'''
    #print 'Getting vertex degree..'
    #self.getVertices()  # ~80sec
    
    ''' Calc Maximum Average Degree of the graph'''
    print 'Getting Maximum Average Degree..'
    self.getMaxAveDegree()
    
    ''' Calc scan statistic 1'''
    print 'Calculating scan statistic 1...'
    self.calcScanStat1()
    
    
  
  ##### ******************** #####
  
  '''
  def getVertices(self): # ~80s
    #self.MVD = 0 # Max vertex degree
    
    start = clock()
    prevVal = float('inf')
    for val in self.G_sparse.indices:
      self.vertices[val].degree += 1
      if val <  
      
    # if self.vertices[val].degree > self.MVD:
    #self.MVD = self.vertices[val].degree
  
    print "\nCalculating vertex degree took: ", (clock() - start), "secs"
  '''
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
  # SCAN STATISTIC 1 #
  ####################
  def calcScanStat1(self):
    '''
    Determine scan statistic of neighborhood n = 1
    '''
    for vertx in self.vertices: 
      # Determine induced subgraph caused by this vertex
      self.getIndSubr(vertx)  
  
  ####################
  # INDUCED SUBGRAPH #
  ####################
  def getIndSubr(self, vertx):
    '''
    Get the induced subgraph of a single vertex
    '''
    
    col = vertx.ind;
    for v in self.G_sparse.indices[self.G_sparse.indptr[col]:self.G_sparse.indptr[col+1]]: # Rows of nnz entries - corresponding to vertices
      vertx.adjList.append(self.vertices[v]) # append vertices. * Vertices still empty containers though
    vertx.indSubgrEdgeNum = len(vertx.adjList) # number of edges
    
    for v in vertx.adjList:
      if self.G_sparse.indices[self.G_sparse.indptr[v.ind]:self.G_sparse.indptr[v.ind+1]]:
	
      
  
  def calcScanStat2(self):
    '''
    Determine scan statistic of neighborhood n = 2
    '''
    pass
  
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
    
  # Unused
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
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/Scan/M87102217_smgr.mat', big = False, sym = True, binarize = True)
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/M87199728_fiber.mat', True, True, True)
  gr.loadgraphMatx('/data/projects/MRN/graphs/biggraphs/M87199728_fiber.mat', True, True, False) # server
  gr.calcGraphInv()
  
  import pdb; pdb.set_trace()

if __name__ == '__main__':
  main()

