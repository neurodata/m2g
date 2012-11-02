#!/usr/bin/python
'''
@author: Disa Mhembere
Determine some graph invariants on big and small graphs
Date: 5 Sept 2012
'''

import scipy.io as sio
import numpy as np
from math import ceil
import scipy.sparse.linalg.eigen.arpack as arpack
import scipy.special

import os
import argparse
import sys
from time import time

import mrpaths
import mrcap.lcc as lcc

import unittesting

from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
from maxavgdeg import getMaxAveDegree
from scanstat_degr import calcScanStat_Degree

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
  

########################
# EIGEN TRIANGLE LOCAL #
########################
# Based on work by: Charalampos E. Tsourakakis
# Published as: Counting Triangles in Real-World Networks using Projections
def eignTriangleLocal(G_fn, lcc_fn = None, roiRootName = None,k=1,  N=1):
  '''
  Local Estimation of Triangle count
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  '''
  print '\nCalculating Eigen triangle count estimation...'
  if (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)
  if (N == 2): # SS2
    G = G.dot(G)+G
  
  # test case
  else:
    G = sio.loadmat(G_fn)['fibergraph']
  
  n = G.shape[0] # number of nodes
  numTri = np.zeros(n) # local triangle count
  
  l, u = arpack.eigs(G, k=G.shape[0]-2, which='LM') # LanczosMethod(A,0) 
  
  for j in range(n):
    numTri[j] = abs(round((sum( np.power(l.real,3) * (u[j][:].real**2)) ) / 2.0))
    
    if (j > 0 and (j % (int(G.shape[0]*0.1)) == 0)):
        print ceil(j / (float(G.shape[0]))*100), "% complete..."
  
  print "100 % complete..."
  
  '''write to file '''
  if (lcc_fn):
    tri_fn = getBaseName(lcc_fn) + '_triangles.npy'
  
  else:  # test
    tri_fn = os.path.join('bench', str(G.shape[0]), 'test_triangles.npy')
    
  np.save(tri_fn, numTri) # save location wrong - Should be invariants
  return tri_fn
  
#####################
# CLUSTERING CO-EFF #
#####################
# Based on work by: Jari Saramaki
# Published as: Generalizations of the clustering coefficient to weighted complex networks
def calcLocalClustCoeff(deg_fn, tri_fn, G_fn = None, lcc_fn = None, roiRootName = None , weighted= False, test=False):
  '''
  deg_fn = full filename of file containing an numpy array with vertex degrees
  tri_fn = full filename of file containing an numpy array with num triangles
  roiRootName - full path of roi + root (i.g. /Users/disa/roi/MXXX_roi)
  lcc_fn - largest connected component full filename (.npy)
  G_fn - fibergraph full filename (.mat)
  '''
  print "\nCalculating local clustering coeff.."
  start = time()
  degArray = np.load(deg_fn)
  triArray = np.load(tri_fn)
  
  ccArray = np.empty_like(degArray)
  
  if len(degArray) != len(triArray):
    print "Lengths of triangle and degree arrays must be equal"
    sys.exit(-1)  
 
  # Weighted graphs 
  if(weighted):
    G = loadAdjMat(G_fn, lcc_fn, roiRootName)  
    
    maxWeight = np.max(G) # max weight of the graph
    maxIdx = G.argmax() #indx of max when flattened
    maxX = maxIdx / G.shape[0] # max x-index
    maxY = maxIdx % G.shape[0]# max y-index
  
  triArr2 = np.empty_like(degArray)
  
  # (3) Jari et al
  for i in range(G.shape[0]):
    cubedRtSum = 0
    triCnt = 0
    w_i = G.indicies[G.indptr[i]:G.indptr[i+1]]
    for k in range(G.shape[0]):
      w_k = G.indicies[G.indptr[k]:G.indptr[k+1]]
      for j in range(G.shape[0]):
        
        if [j,k] not in w_i:
          break # No edge
        if [j] not in w_k:
          break # No edge
        
        iNeigh = G.indices[G.indptr[i]:G.indptr[i+1]]
        idx_ij = np.where( iNeigh == j)[0][0]
        idx_ik = np.where( iNeigh == k)[0][0]
        idx_jk = np.where( G.indices[G.indptr[k]:G.indptr[k+1]] == j)[0][0]
      
        cubedRtSum += scipy.special.cbrt( (G.data[G.indptr[i]:G.indptr[i+1]][idx_ij])/float(maxWeight) * \
          (G.data[G.indptr[i]:G.indptr[i+1]][idx_ik])/float(maxWeight) *\
          (G.data[G.indptr[k]:G.indptr[k+1]][idx_jk])/float(maxWeight) )
        triCnt += 1
    
    ccArray[i] = cubedRtSum
    triArr2[i] = triCnt
  
  # Binarized graphs 
  else:
    for u in range (len(degArray)):
      if (degArray[u] > 2):
        ccArray[u] = (2.0 * triArray[u]) / ( degArray[u] * (degArray[u] - 1) ) #(1) Jari et al
      else:
        ccArray[u] = 0

  ccArr_fn =  getBaseName(tri_fn) +'_clustcoeff.npy'
  
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
  # TODO: DM
  pass


####################
# SCAN STATISTIC 2 #
####################

def calcScanStat2():
  '''
  #TODO: DM
  '''
  pass

  
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


#########################  ************** #########################
###########
# TESTING #
###########

def testing():
  G_fn = sys.argv[1]  # Name of the graph file - format .npy
  dataDir = sys.argv[2]   # Name of the dir where you want the result to go
  
  mad = getMaxAveDegree(G_fn, lcc_fn = None)
  ss1_fn, deg_fn, numNodes = calcScanStat_Degree(G_fn, lcc_fn = None, roiRootName = None, N=1)
  
  sys.exit(-1)
  
  #tri_fn = calcNumTriangles(ss1_fn, deg_fn, lcc_fn = None)
  tri_fn = eignTriangleLocal(G_fn)
  #ccArr_fn = calcLocalClustCoeff(deg_fn, tri_fn, test=True)
  
  testObj = unittesting.test(G_fn, dataDir, numNodes, ss1_fn = ss1_fn, deg_fn = deg_fn, tri_fn = tri_fn, ccArr_fn = None, mad = mad) # Create unittest object
  #testObj.testSS1()
  #testObj.testDegree()
  testObj.testTriangles()

#########################  ************** #########################
#########################  ************** #########################
  
def realgraph():
  gr = graph()
  G_fn = '/home/disa/testgraphs/big/M87102217_fiber.mat'
  lcc_fn = '/home/disa/testgraphs/lcc/M87102217_concomp.npy'
  roiRootName = '/home/disa/testgraphs/roi/M87102217_roi'
  gr.loadgraphMatx(G_fn, True, True, False) # mrbrain big

  ''' Calc Scan Stat 1 '''
  #ss1Array, degArray = calcScanStat_Degree(G_fn, lcc_fn, roiRootName, N=1)

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



'''
# Not so important invariant
##################
# AVERAGE DEGREE #
##################

def getAveDegree(vertDegArr):
  
  #Calculate the Average Degree of a vertex
  #vertDegArr - numpy array of vertex degrees
  #Returns:
  #=========
  #The Average degree of a vertex
  
  print "\nCalculating Average degree..."
  return np.average(vertDegreArr)
'''