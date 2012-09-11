'''
@author: Disa Mhembere
Determine some graph invariants on big and small graphs
Date: 5 Sept 2012
'''

import scipy.io as sio
import numpy as np
import os
import argparse

class graph():
  def __init__(self, maxAveDeg):
    '''
    self.G - Adjacency matrix
    self.size - Number of edges
    self.classification - This is big or small
    self.binarize - Whether the graph is binarized or not
    self.sym - Whether the graph is symmeterized or not
    
    self.G_sparse
    self.G_dense
    self.vertices
    '''
    self.maxAveDeg = maxAveDeg

  def loadgraphMatx(self, graph_fn, big = False, sym = False, binarize = False, toPyMat = False):
    ''' 
    load a graph. symmeterize, binarize & convert to python matrix if specified
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
       
    # self.G = self.G_sparse.todense() # unpack graph
      
    self.G = self.G_sparse.data
    self.indices = self.G_sparse.indices
      
    if(self.binary):      
      self.G[:] = 1 # All non-zero entries set to one
            
    if(sym):
      self.G = self.G + self.G.T
      
    self.size = self.G_sparse.getnnz() # Number of edges in graph
      
    if (toPyMat):
      if (big):
	print 'Cannot convert \'big\' matrix to python matrix!'
      else:
	self.G = self.G.tolist() # turn into python list of lists

  def calcGraphInv(self):
    '''
    Calculate several graph invariants
    1. The maximum average degree (MAD) of the graph
    2. 
    '''
    self.vertices = np.array(vertex())
    self.vertices = np.tile(self.vertices, self.G_sparse.shape[0])
    
    ''' Get the degree of each vertex in the graph'''
    getVertexDegree()
    
    ''' Calc Maximum Average Degree of the graph'''
    getMaxAveDegree()
  
  def getVertexDegree(self):
    '''
    Calc the degree of each vertex in the graph
    '''
    for val in self.G_sparse.indices:
      self.vertices[val].degree += 1    
  
  def getMaxAveDegree(self):
    '''
    Calc the Max Average Degree of the graph
    '''
    self.MAD = 0 
    for vertex in self.vertices:
      vertex.indSubgrSize = vertex.degree - 1 # STUB - setting induced subgraph size
      aveDeg = vertex.getAveDegree()
      if aveDeg > self.MAD:
	self.MAD = aveDeg
  
  def calcIndSubgr(self):
      pass
  
  
    
class vertex():
  '''
  Class to hold a vertex object
  '''
  def __init__(self, degree = 0):
    self.degree = degree
    self.indSubgrSize = 0 # size of enduced subgraph
    
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

  








def main():
  gr = graph()
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/Scan/M87102217_smgr.mat', False, True, True)
  gr.loadgraphMatx('/Users/dmhembere44/Downloads/M87199728_fiber.mat', False, True, True)
  gr.calcMAD()
  gr.calcGraphInv()

if __name__ == '__main__':
  main()

