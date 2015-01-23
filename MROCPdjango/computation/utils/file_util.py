#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# file_util.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu

"""
A script containing useful file related operations that are performed
with frequency.
"""

import os

def makeDirIfNone(dirname):
  '''
  Make a directory if none exists already

  positional args:
  ================
  dirname - the directory to be created
  '''
  if os.path.exists(dirname):
    return
  else:
    os.makedirs(dirname)


def createSave(fn, content):
  '''
  Wrapper for numpy.save(fn, content)
  but creates the dir if not already there

  positional args:
  ================
  fn - file name
  content - numpy saveable file
  '''
  from numpy import save

  makeDirIfNone(os.path.dirname(fn))
  save(fn, content)

def getPathLeaf(path):
  '''
  Get the leaf of a path

  positional args:
  ================
  path - the full path of which you want to extract the leaf
  '''
  import ntpath

  head, tail = ntpath.split(path)
  return tail

def loadAnyMat(fn, data_elem=None):
  '''
  Load up arbitrary.mat matrix as a csc matrix

  positional args:
  ================
  fn - the filename

  optional args:
  ================
  data_elem - the data element item name
  '''
  from scipy.io import loadmat
  from scipy.sparse import csc_matrix as csc
  from numpy import float32, float64

  try:
    G = loadmat(fn)
  except Exception:
    return "[ERROR]: Could not load the file from disk. *NOTE: Cannot load matrices with 0 stored entries."

  if data_elem:
    try:
      G = G[data_elem]
    except:
      return "[IOERROR]: The data element '%s' you provided was not found." % data_elem

  else:
    key = set(G.keys()) - set(['__version__', '__header__', '__globals__'])
    key = list(key)
    if len(key) > 1:
      return "[ERROR]: Too many data elements to distinguish the graph - use only one data element or specify explicitly"
    else:
      G = G[key[0]]

  # Ensure float64 type
  if not (isinstance(G[0,0], float32) and isinstance(G[0,0], float64) and isinstance(G, csc)):
    G = csc(G, dtype=float32)

  return G

def recursive_listdir(drcty, hidden=False):
  """
  Recursively list a directory.
  *NOTE - only includes filenames not starting with . and whose extension has 2 or less chars

  positional args:
  ================
  drcty - the directory to recursively list

  optional args:
  ==============
  hidden - Include hidden directories in the listing
  """

  filelist = []
  for top, dirs, files in os.walk(drcty):
    for nm in files:
      if hidden:
        filelist.append(os.path.join(top, nm)) # add no matter what when hidden is true

      elif not nm.startswith(".") and len(os.path.splitext(nm)[1]) <= 3: # only add if not hidden
        filelist.append(os.path.join(top, nm))
  return filelist