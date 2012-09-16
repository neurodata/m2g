'''
@author: Disa Mhembere
Determine some graph invariants on big and small graphs
Date: 5 Sept 2012
'''

import scipy.io as sio
import numpy as np
import os
import argparse

import scipy.sparse as scsp

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
 
 
    #self.G = self.G_sparse.data
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
	self.G = self.G.tolist() # turn into python list of lists
  
  def symmetrize(self):
    '''
    Symmetrize an upper/lower triangular matrix
    '''
    self.G_sparse = self.G_sparse + self.G_sparse.T
    self.sym = True if not (self.sym) else self.sym
  
  def calcGraphInv(self):
    '''
    Calculate several graph invariants
    1. The maximum average degree (MAD) of the graph
    2. 
    '''
    self.vertices = np.array(vertex())
    self.vertices = np.tile(self.vertices, self.G_sparse.shape[0])
    
    ''' Get the degree of each vertex in the graph'''
    print 'Getting vertex degree..'
    self.getVertexDegree()  # Slow...
    
    ''' Calc Maximum Average Degree of the graph'''
    print 'Getting Maximum Average Degree..'
    self.getMaxAveDegree()
  
  
  
  
  def getVertexDegree(self): # Slow...
    '''
    Calc the degree of each vertex in the graph
    '''
    
    start = clock()
    
    for val in self.G_sparse.indices:
      self.vertices[val].degree += 1
    
    print "Time taken: ", (clock() - start)
  
  def getMaxAveDegree(self):
    '''
    Calc the Eigenvalue Max Average Degree of the graph
    Note this is an estimation and is guaranteed to be greater than or equal to the true MAD
    '''
    if not self.sym:
      self.symmetrize() # Make sure graph is symmetric
      
    self.eigvals = scsp.linalg.eigen(self.G)[0] # get eigenvalues
    self.maxAveDeg =  self.eigvals.max() # Est. MAD is the max eigenvalue
  
  def calcScanStat1(self):
    '''
    Determine scan statistic of neighborhood n = 1
    '''
    #for vertx in self.vertices
    
    pass
  
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
    
class vertex():
  '''
  Class to hold a vertex object
  '''
  def __init__(self, degree = 0):
    self.degree = degree
    #self.adjList = np.array([])
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
  #gr.loadgraphMatx('/Users/dmhembere44/Downloads/M87199728_fiber.mat', True, True, True)
  gr.loadgraphMatx('/data/projects/MRN/graphs/biggraphs/M87199728_fiber.mat', True, True, False) # server
  gr.calcGraphInv()
  
  import pdb; pdb.set_trace()

if __name__ == '__main__':
  main()

