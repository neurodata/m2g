#!/usr/bin/python

# passload.py
# Created by Disa Mhembere on 2013-02-25.
# Copyright (c) 2013. All rights reserved.

# Module to load up sensitive data

import os

def loadpass(fn = os.path.join(os.path.dirname(__file__), 'utils.data')):
  '''
  Load up a dict with sensitive info
  @param fn: the filename containing correctly formatted data

  *IMPORTANT: fn format attr_name:attr_val [on single line for each attr]
  '''
  fdata =  open(fn,'r').read()

  fdata = fdata.strip().split("\n") # Each attribute on a single line
  fdict = {}

  for entry in fdata:
    e = entry.split(":")
    try:
      fdict[e[0]] = e[1]
    except:
      import pdb; pdb.set_trace()

  print fdict
  return fdict

if __name__ == '__main__':
  loadpass()
