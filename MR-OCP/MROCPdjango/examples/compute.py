#!/usr/bin/env python
#
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
# Created by Disa Mhembere
# Email: disa@jhu.edu
# @Author: Disa Mhembere
# Example code of how to upload a previously built
# graph and run some invariants on it.

import urllib2
import argparse
import sys
import os

import zipfile
import tempfile

import webbrowser

def main():
  parser = argparse.ArgumentParser(description='Upload a single or multiple graphs. If multiple please \
      zip into a single dir. Base url -> http://www.openconnecto.me/graph-services/graphupload/')
  parser.add_argument('url', action="store", help='url is http://mrbrain.cs.jhu.edu/graph-services/graphupload/')
  parser.add_argument('webargs', action="store", help='comma separated list (no spaces) of invariant \
      types. E.g cc,tri,deg,mad,eig,ss1 for clustering coefficient, triangle count, degree, maximum \
      average degree, eigen-pairs & scan statistic')
  parser.add_argument('file', action="store", help ='Single graph or a Zipped directory with one\
      or more graphs')
  parser.add_argument('inputFormat', action='store', help='Input format of the graph i.e. One of: \
      graphml | ncol | edgelist | lgl | pajek | graphdb | numpy | mat')
  parser.add_argument('--convertToFormat', '-c', action='store', help='Convert the resulting annotated \
      graph to other formats. This is a comma separated list (no spaces) of convert formats. Format \
      graphml is produced by default, but you can convert to: ncol | edgelist | lgl | pajek | dot | gml | leda)')
  parser.add_argument('-a', '--auto', action="store_true", help="Use this flag if you want a browser \
      session to open up with the result automatically")
  result = parser.parse_args()

  if not (os.path.exists(result.file)):
    print "Invalid file name. Check the folder: " + result.file
    sys.exit()
  else:
    print "Loading file into memory.."

  # Create a temporary file to store zip contents in memory
  tmpfile = tempfile.NamedTemporaryFile()
  zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)

  zfile.write(result.file)
  zfile.close()

  tmpfile.flush()
  tmpfile.seek(0)
  print "File uploaded .."

#  Testing only: check the contents of a zip file.
#
#    rzfile = zipfile.ZipFile(tmpfile.name, "r", allowZip64=True)
#    ret = rzfile.printdir()
#    ret = rzfile.testzip()
#    ret = rzfile.namelist()
#    import pdb; pdb.set_trace()

  result.url = result.url if result.url.endswith('/') else result.url + '/' #
  result.webargs = result.webargs if result.webargs.endswith('/') else result.webargs + '/'

  if result.convertToFormat:
    result.inputFormat = result.inputFormat if result.inputFormat.endswith('/') else result.inputFormat + '/'

  result.convertToFormat = "" if not result.convertToFormat else result.convertToFormat


  try:
    ''' **IMPORTANT: THIS IS HOW TO BUILD THE URL** '''
    req = urllib2.Request ( result.url + result.webargs + result.inputFormat + result.convertToFormat, tmpfile.read() )
    print "Calling url ..."
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read())
    sys.exit(0)

  msg = response.read() # This is how to get the response
  print msg

  if result.auto:
    ''' Open up a tab in your browser to view results'''
    webbrowser.open(msg.split(' ')[3]) # This might change

if __name__ == "__main__":
  main()
