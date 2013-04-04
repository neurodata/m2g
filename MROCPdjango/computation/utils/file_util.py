#!/usr/bin/python

# file_util.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

# make a directory if none exists

import os

def makeDirIfNone(dirname):
  '''
  Make a directory if none exists already

  @param dirname: the directory to be created
  '''
  if os.path.exists(dirname):
    return
  else:
    os.makedirs(dirname)


def createSave(fn, content):
  '''
  Wrapper for numpy.save(fn, content)
  but creates the dir if not already there

  @param fn: file name
  @param content: numpy saveable file
  '''
  from numpy import save

  makeDirIfNone(os.path.dirname(fn))
  save(fn, content)

def getPathLeaf(path):
  '''
  Get the leaf of a path
  @param path: the full path of which you want to extract the leaf
  '''
  import ntpath

  head, tail = ntpath.split(path)
  return tail

def loadAnyMat(fn, data_elem=None):
  '''
  Load up arbitrary.mat matrix as a csc matrix
  @param fn: the filename
  @param data_ele: the data element item name
  '''
  from scipy.io import loadmat
  from scipy.sparse import csc_matrix as csc

  G = loadmat(fn)
  if data_elem:
    try:
      G = G[data_elem]
    except:
      return "[IOERROR]: The data element '%s' you provided was not found." % data_elem

  else:
    key = list(set(G.keys()) - set(['__version__', '__header__', '__globals__']))
    if len(key) > 1:
      return "[ERROR]: Too many data elements to distinguish the graph - use only one data element or specify explicitly"

  if not isinstance(G, csc):
    G = csc(G)
  return G
