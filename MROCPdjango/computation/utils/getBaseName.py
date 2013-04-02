#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Get the base name of MRN dataset graphs

import os
import argparse

def getBaseName(fn):
  if fn.endswith('/'):
    fn = fn[:-1]
  return (os.path.splitext(fn.split('/')[-1])[0]).partition('_')[0]

def main():

    parser = argparse.ArgumentParser(description='Get the base name of MRN dataset graphs')
    parser.add_argument('fn', action='store',help='The full path filename')

    result = parser.parse_args()
    getBaseName(result.fn)

if __name__ == '__main__':
  main()

def getBaseName(fn):
  if fn.endswith('/'):
    fn = fn[:-1]
  return (os.path.splitext(fn.split('/')[-1])[0]).partition('_')[0]