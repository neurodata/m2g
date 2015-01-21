#!/usr/bin/python

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


# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012

"""
Get the base name of MRN dataset graphs
"""

import os
import argparse

def getBaseName(fn):
  """
  Get the base name of a given filename.
  Given: M89345_fiber.dat, return should be M89345 as basename

  positional args:
  ================
  fn - the filename

  returns:
  ========
  basename
  """
  if fn.endswith('/'):
    fn = fn[:-1]
  return (os.path.splitext(fn.split('/')[-1])[0]).partition('_')[0]

def main():
  """
  CL parser and caller function
  """
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