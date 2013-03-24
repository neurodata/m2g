#!/usr/bin/python

# vert_edge_deg_ss_cc.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

import os
from scipy.io import loadmat
import numpy as np
from math import ceil

from computation.utils import getBaseName # Duplicates right now
from computation.utils import loadAdjMatrix # Duplicates right now
from computation.utils.file_util import createSave

import argparse
from time import time


def vert_edge_deg_ss_cc(G_fn, G=None, lcc_fn=None, verDir=None, edgeDir=None,\
                        degDir=None, ss1Dir=None, ccDir=None, N=1, ver=False, \
                        edge=False, deg=False, ss1=False, cc=False, numTri=None, vertxDeg=None):
  '''
  @param G_fn: fibergraph full filename (.mat)
  @param G: the sparse matrix containing the graphs
  @param lcc_fn: largest connected component full filename (.npy)
  @param verDir: Directory where to place the global vertex count result
  @param edgeDir: Directory where to place local edge number result
  @param degDir: Directory where to place local degree result
  @param ss1Dir: Directory where to place scan statistic result
  @param ccDir: Directory where to place clustering coefficient result
  @param N: Scan statistic number i.e 1 or 2 ONLY

  @param ver: Count global vertices? True for yes else False. If verDir assumed to be True
  @param edge: Count global edges? True for yes else False. If edgeDir assumed to be True
  @param deg: Compute local degree? True for yes else False. *NOTE BE CALLED EXPLICTLY TO BE DONE!
  @param ss1: Compute scan stat. True for yes else False. If ss1Dir asssumed to be True
  @param cc: True for yes else False. If ccDir assumed to be True
  @param numTri: either the #triangle npy array or the file name of it (used for cc)
  @param vertxDeg: either the deg npy array or the file name of it (used for cc)

  @return returnDict: a dict with the attribute & its filename # TODO: May change
  '''

  returnDict = dict() # dict to be returned

  if (G !=None):
    pass
  elif (lcc_fn):
    G = loadAdjMat(G_fn, lcc_fn)
  # test case
  else:
    G = loadmat(G_fn)['fibergraph']

  numNodes = G.shape[0]

  ''' Initialize computation variables '''
  if (verDir or ver):
    numVertices = numNodes

  if (ss1Dir or ss1):
    indSubgrEdgeNum = np.zeros(numNodes) # Induced subgraph edge number i.e scan statistic

  # Complex case where #triangles & degree might be passed
  if (ccDir or cc):
    from eigs_mad_deg_tri import eigs_mad_deg_tri

    # if either #tri or deg is undefined
    if not (numTri or vertxDeg):
      # run other code to get em
      if not numTri and vertxDeg:
        numTri = eigs_mad_deg_tri(G_fn, G, lcc_fn, triDir=None, tri=True)['tri_fn'] # SAVES TO DEFAULT LOCATION
      if not vertxDeg and numTri:
        vertxDeg = eigs_mad_deg_tri(G_fn, G, lcc_fn, degDir=None, deg=True)['deg_fn'] # SAVES TO DEFAULT LOCATION
      else:
        res = eigs_mad_deg_tri(G_fn, G, lcc_fn, triDir=None, degDir=None, deg=True, tri=True) # SAVES TO DEFAULT LOCATION
        numTri = res['tri_fn']
        vertxDeg = res['deg_fn']

    # load/get the number of triangles if defined.
    if numTri:
      numTri = numTri if isinstance(numTri, np.ndarray) else np.load(numTri)
    if vertxDeg:
      vertxDeg = vertxDeg if isinstance(vertxDeg, np.ndarray) else np.load(vertxDeg)

    ccArray = np.empty_like(vertxDeg)

  # Degree count
  if (degDir or deg):
    vertxDeg = np.zeros(numNodes) if vertxDeg is None else vertxDeg

  # Edge count
  if (edgeDir or edge):
    numEdges = 0 if not vertxDeg else np.sum(vertxDeg)
    edges_done = True if not (numEdges == 0) else False

  # Check if computation has already been done
  vertx_done = False if np.all(vertxDeg) == 0 else True # Always defined so this is OK

  ''' Perform computation '''
  percNodes = int(numNodes*0.1)
  mulNodes = float(numNodes)

  start = time()
  for vertx in range (numNodes):
    if (vertx > 0 and (vertx % (percNodes) == 0)):
      print ceil((vertx/mulNodes)*100), "% complete..."

    if locals().has_key('indSubgrEdgeNum'):
      nbors = G[:,vertx].nonzero()[0]
      if (nbors.shape[0] > 0):
        nborsAdjMat = G[:,nbors][nbors,:]

        indSubgrEdgeNum[vertx] = nbors.shape[0] + (nborsAdjMat.nnz/2.0)  # scan stat 1 # Divide by two because of symmetric matrix
      else:
        indSubgrEdgeNum[vertx] = 0 # zero neighbors hence zero cardinality enduced subgraph

    if (deg and not vertx_done): # TODO: Note this explict deg must be used
      vertxDeg[vertx] = G[:,vertx].nonzero()[0].shape[0] # degree of each vertex #TODO check if slow

    if locals().has_key('ccArray'):
      if (vertxDeg[vertx] > 2):
        ccArray[vertx] = (2.0 * numTri[vertx]) / ( degArray[vertx] * (degArray[vertx] - 1) ) # Jari et al
      else:
        ccArray[vertx] = 0

    if (locals().has_key('numEdges') and (not edges_done) and (not deg)):
      numEdges += G[:,vertx].nonzero()[0].shape[0]

  if locals().has_key('ccArray'):
    ccArray = ccArray*3 # Since cc is concerned with the true number of triangles counted - we include duplicates

  if (locals().has_key('numEdges')):
    numEdges = numEdges if not numEdges == 0 else np.sum(vertxDeg)

  print "100 % complete"
  print "Time taken for invariants: %f secs" % float(time() - start)

  # computation complete - handle saving now ...
  ''' Degree count'''
  if (deg):
    degDir = os.path.join(os.path.dirname(G_fn), "Degree") if degDir is None else degDir
    deg_fn = os.path.join(degDir, getBaseName(G_fn) + '_degree.npy')
    createSave(deg_fn, vertxDeg) # save it
    returnDict['deg_fn'] = deg_fn # add to return dict
    print 'Degree saved ...'

  if locals().has_key('indSubgrEdgeNum'):
    ss1Dir = os.path.join(os.path.dirname(G_fn), "SS1") if ss1Dir is None else ss1Dir
    ss1_fn = os.path.join(ss1Dir, getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    createSave(ss1_fn, indSubgrEdgeNum) # save it
    returnDict['ss1_fn'] = ss1_fn # add to return dict
    print 'Scan 1 statistic saved ...'

  if locals().has_key('numVertices'):
    vertDir = os.path.join(os.path.dirname(G_fn), "Globals") if vertDir is None else vertDir
    ver_fn = os.path.join(vertDir, getBaseName(G_fn) + '_numvert.npy')
    createSave(ver_fn, numVertices) # save it
    returnDict['ver_fn'] = ver_fn # add to return dict
    print 'Global vertices number saved ...'

  if locals().has_key('numEdges'):
    edgeDir = os.path.join(os.path.dirname(G_fn), "Globals") if edgeDir is None else edgeDir
    edge_fn = os.path.join(edgeDir, getBaseName(G_fn) + '_numedges.npy')
    createSave(edge_fn, numEdges) # save it
    returnDict['edge_fn'] = edge_fn # add to return dict
    print 'Global edge number saved ...'

  if locals().has_key('ccArray'):
    ccDir = os.path.join(os.path.dirname(G_fn), "ClustCoeff") if ccDir is None else ccDir
    cc_fn = os.path.join(ccDir, getBaseName(G_fn) + '_clustcoeff.npy')
    createSave(cc_fn, ccArray) # save it
    returnDict['cc_fn'] = cc_fn # add to return dict
    print 'Clustering coefficient saved ...'

  else: # test
    ss1_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_scanstat'+str(N)+'.npy')
    deg_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_degree.npy')
    ccArr_fn = os.path.join('bench', str(G.shape[0]), getBaseName(G_fn) + '_clustcoeff.npy')
    # We dont test the vert & edges

  # del vertxDeg, indSubgrEdgeNum --> consider
  return returnDict # used to return --> return [ss1_fn, deg_fn, G.shape[0]]

#def main():
#
#    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
#    parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
#    parser.add_argument('lcc_fn', action='store',help='Full filename of largest connected component (.npy)')
#    parser.add_argument('ss1Dir', action='store', help='Full path of directory where you want Scan stat .npy array resulting file to go')
#    parser.add_argument('degDir', action='store', help='Full path of directory where you want Degree .npy array resulting file to go')
#
#    result = parser.parse_args()
#
#    vert_edge_deg_ss_cc(result.G_fn, None, result.lcc_fn, result.ss1Dir, result.degDir)

if __name__ == '__main__':
  print 'This file is not to be called directly. Use helpers'
