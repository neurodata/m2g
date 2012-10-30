#!/usr/bin/python
'''
@author: Disa Mhembere
Determine some graph invariants on big and small graphs
Date: 5 Sept 2012
'''
import math
import scipy.io as sio
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack

import os
import argparse
import sys
from time import time

import mrpaths
import mrcap.lcc as lcc

import unittesting

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

  def loadgraphMatx(self, graph_fn, big = False, sym = True, binarize = False, toPyMat = False):
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
  
#################################
# MAX AVERAGE DEGREE EIGENVALUE #
#################################
    
def getMaxAveDegree(G_fn, lcc_fn = None, roiRootName = None):
  '''
  Calc the Eigenvalue Max Average Degree of the graph
  Note this is an estimation and is guaranteed to be greater than or equal to the true MAD
  G_fn - filename of the graph .npy
  lcc_fn - largest connected component of the graph. If none then this is a test case. .npy file
  '''
  if lcc_fn:
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
    
  # test case
  else:    
    try:
      G = sio.loadmat(G_fn)['fibergraph']
    except:
      print "file not found %s" % G_fn

  
  #import pdb; pdb.set_trace()
  start = time()
    # LR = Largest Real part
  
  maxAveDeg = (np.max(arpack.eigs(G, which='LR')[0])).real # get eigenvalues, then +ve max REAL part is MAD eigenvalue estimation
  print "Maxium average degree = ", maxAveDeg

##################
# AVERAGE DEGREE #
##################

def getAveDegree(vertDegArr):
  '''
  Calculate the Average Degree of a vertex
  vertDegArr - numpy array of vertex degrees
  Returns:
  =========
  The Average degree of a vertex
  '''
  return np.average(vertDegreArr)

###################
# SCAN STATISTICS #
###################
def calcScanStat(G_fn, lcc_fn = None, roiRootName = None ,bin = False, N=1):
  '''
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  bin - binarize or not
  N - Scan statistic number i.e 1 or 2 ONLY
  '''
  print 'Calculating scan statistic %d...' % N
  
  if (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn)
  if (N == 2):
    G = G.dot(G)+G
  
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
    
  vertxDeg = np.zeros(G.shape[0]) # Vertex degrees of all vertices
  indSubgrEdgeNum = np.zeros(G.shape[0]) # Induced subgraph edge number i.e scan statistic

  for vertx in range (G.shape[0]):
    if (vertx > 0 and (vertx% (int(G.shape[0]*0.1)) == 0)):
        print ceil(vertx/(float(G.shape[0]))*100), "% complete..."

    nbors = G[:,vertx].nonzero()[0]
    vertxDeg[vertx] = nbors.shape[0] # degree of each vertex
 
    if (nbors.shape[0] > 0):
      nborsAdjMat = G[:,nbors][nbors,:]
      indSubgrEdgeNum[vertx] = nbors.shape[0] + nborsAdjMat.nnz # scan stat 1
    else:
      indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph

  '''write to file '''
  if (lcc_fn):
    ss1_fn = getbaseName(lcc_fn) + '_scanstat'+str(N)+'.npy'
    deg_fn = getbaseName(lcc_fn) + '_degree.npy'
  
  else:  
    ss1_fn = os.path.join('bench', str(G.shape[0]), 'test_scanstat')+ str(N)+'.npy'
    deg_fn = os.path.join('bench', str(G.shape[0]),'test_degree.npy')
    
    
  np.save(ss1_fn, indSubgrEdgeNum) # save location wrong - Should be invariants
  np.save(deg_fn, vertxDeg)  # save location wrong - Should be invariants
    
  # del vertxDeg, indSubgrEdgeNum
  return [ss1_fn, deg_fn, G.shape[0]] #return scan stat1, degree of each node, the number of nodes in the graph

#######################
# NUMBER OF TRIANGLES #
#######################
def calcNumTriangles(ss1Array, degArray, lcc_fn = None):
  print 'Counting the number of triangles...'
  start = time()
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
  
  for e in range (len(triangles)-1):
    if triangles[e] < 0:
      print "Vertex:", e , ", Value: ", triangles[e]    
  
  if (lcc_fn):
    triArr_fn =  getbaseName(lcc_fn) +'_triangles.npy'
  else:
    triArr_fn =  os.path.join('bench', str(len(triangles)),'test_triangles.npy')
    
  np.save(triArr_fn, triangles)  # save location wrong!
  
  print 'Time taken to calc Num triangles: %f secs\n' % (time() - start)
  #del triangles
  return triArr_fn

########################
# EIGEN TRIANGLE LOCAL #
########################

def eignTriangleLocal(G_fn, lcc_fn = None, roiRootName = None,k=1,  N=1):
  '''
  DM: TODO
  '''
  
  if (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn)
  if (N == 2): # SS2
    G = G.dot(G)+G
  
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
  
  n = G.shape[0] # number of nodes
  numTri = np.zeros(n) # local triangle count
  
  #eigval, eigvect = arpack.eigs(G, k=G.shape[0]-2, sigma='real', which='LM', OPpart='r') # LanczosMethod(A,0) 
  eigval, eigvect = arpack.eigs(G, k=G.shape[0]-2, which='LM') # LanczosMethod(A,0) 
  #import pdb; pdb.set_trace()
  
  l = np.diag(eigvect.real).conj()
  l = (np.matrix(l)).T
  
  import pdb; pdb.set_trace()
  
  for j in range(n):
    numTri[j] = (sum( np.power(l,3) * (eigval[j:].real**2)) ) / 2.0
  
  #import pdb; pdb.set_trace()
  
  #Alf = abs(eigval[0].real) # has real & img
  #U = eigvect[0] # has real & img

  #i = 1
  #loop = True
  #while (loop and i <= (G.shape[0]-2)):
    
  #  eigval, eigvect = arpack.eigs(G, k = i) # LanczosMethod(A,i) 
    
  #  Alf = abs(eigval[0].real) # ?????
  #  U = eigval[0] # ?????
  #  i += 1
  #  print "i = ", i
    
  #  bound = abs(pow(eigval[i-2].real,3)) / sum(pow(eigval[:i-2].real,3))
  #  if (bound <= 0 or bound <= tol): 
  #    loop = False
  
  #for j in range(n-2):
  #  numr = 0
  #  for k in range(i-2):
  #   
  #    numTri[j] += ( pow(eigvect[j][k].real,2)*pow(eigval[k],3) ) / 2
  

####################
# Base name getter #
####################
def getbaseName(fn):
  return fn.partition('_')[0]

##########################
# Load Adj mat from lcc #
#########################
def loadAdjMat(G_fn, lcc_fn, roiRootName = None):
  '''
  Load adjacency matrix given lcc_fn & G_fn. lcc has z-indicies corresponding to the lcc :
  G_fn - the .mat file holding graph
  lcc_fn - the largest connected component .npy z-ordering
  '''
  if not roiRootName:
    roiRootName = G_fn.split('_')+'_roi'
       
  vcc = lcc.ConnectedComponent(fn = lcc_fn)
  try:
    fg = lcc._load_fibergraph(roiRootName , G_fn) 
    G = vcc.induced_subgraph(fg.spcscmat)
    G = G+G.T # Symmetrize
  except:
    print "Problem loading real lcc & graph"
    
  return G
  
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

#####################
# CLUSTERING CO-EFF #
#####################
def calcLocalClustCoeff(deg_fn, tri_fn, test=False):
  '''
  deg_fn = full filename of file containing an numpy array with vertex degrees
  tri_fn = full filename of file containing an numpy array with num triangles
  '''
  start = time()
  degArray = np.load(deg_fn)
  triArray = np.load(tri_fn)
  
  ccArray = np.empty_like(degArray)

  if len(degArray) != len(triArray):
    print "Lengths of triangle and degree arrays must be equal"
    sys.exit(-1)  
 
  for v in range (len(degArray)): 
    if (degArray[v] > 0):
      maxEdges = int((degArray[v]+1)*(degArray[v]))/2   # +1 to include the vertex in question. Formula: (n(n-1))/2
      maxNumTri = maxEdges - degArray[v]
      angles = maxNumTri - triArray[v]

      ccArray[v] = triArray[v]/(triArray[v] + angles) # Eq. 2.12
    else:
      ccArray[v] = 0
  
  joiner = "test" if (test) else ""
  
  ccArr_fn = getbaseName(deg_fn) +joiner+'_clustcoeff.npy'
  np.save(ccArr_fn, ccArray)  # save location wrong!
  
  print 'Time taken to calc Num triangles: %f secs\n' % (time() - start)    
  return ccArr_fn
  
###############
# PATH LENGTH #
###############

def pathLength():
  '''
  Path length between each pair of vertices
  '''
  pass

#########################  ************** #########################
###########
# TESTING #
###########

def testing():
  G_fn = sys.argv[1]  # Name of the graph file - format .npy
  dataDir = sys.argv[2]   # Name of the dir where you want the result to go
  
  #mad = getMaxAveDegree(G_fn, lcc_fn = None) 
  #ss1_fn, deg_fn, numNodes = calcScanStat(G_fn, lcc_fn = None, roiRootName = None ,bin = False, N=1)
  #tri_fn = calcNumTriangles(ss1_fn, deg_fn, lcc_fn = None)
  tri_fn = eignTriangleLocal(G_fn)
  
  testObj = unittesting.test(G_fn, dataDir, numNodes, ss1_fn = ss1_fn, deg_fn = deg_fn, tri_fn = tri_fn, ccArr_fn = None, mad = mad) # Create unittest object
  testObj.testSS1()
  testObj.testDegree()
  testObj.testTriangles()
  
  
  '''
  ccArr_fn = calcLocalClustCoeff(deg_fn, tri_fn, test=True)
  
  '''
  
def realgraph():
  gr = graph()
  G_fn = '/home/disa/testgraphs/big/M87102217_fiber.mat'
  lcc_fn = '/home/disa/testgraphs/lcc/M87102217_concomp.npy'
  roiRootName = '/home/disa/testgraphs/roi/M87102217_roi'
  gr.loadgraphMatx(G_fn, True, True, False) # mrbrain big

  ''' Calc Scan Stat 1 '''
  #ss1Array, degArray = calcScanStat(G_fn, lcc_fn, roiRootName ,bin = False, N=1)

  ''' Calc number of triangles'''
  ss1Array = '/home/disa/testgraphs/lcc/M87102217_scanstat1.npy'
  degArray = '/home/disa/testgraphs/lcc/M87102217_degree1.npy'
  triArray = calcNumTriangles(ss1Array, degArray, G_fn)

  '''
    if (self.classification == 'small'):
      printVertInv(ss1Array, 'Scan Statistic 1') # print scan stat 1
      printVertInv(degArray, 'Vertex Degree') # print vertex degree
      printVertInv(triArray, 'Number of triangles') # print number triangles 
    '''
    

def main():
  testing()


if __name__ == '__main__':
  main()
