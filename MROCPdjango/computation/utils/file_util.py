#!/usr/bin/python

# file_util.py
# Created by Disa Mhembere on 2013-03-21.
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

# make a directory if none exists

import os
from numpy import save

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
  makeDirIfNone(os.path.dirname(fn))
  save(fn, content)
