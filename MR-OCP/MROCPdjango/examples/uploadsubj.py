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
  parser = argparse.ArgumentParser(description='Upload a zipped graph (This is script automatically zips).\
      Base url -> http://www.openconnecto.me/graph-services/graphupload/')
  parser.add_argument('url', action="store", help='url is http://www.openconnecto.me/graph-services/graphupload/')
  parser.add_argument('file', action="store", help ='The uncompressed graph file location')
  parser.add_argument('email', action="store", help ='The email address for the result to be sent')
  parser.add_argument('input_format', action='store', help='Input format of the graph i.e. One of: \
      graphml | ncol | edgelist | lgl | pajek | graphdb | numpy | mat')
  parser.add_argument('-i', '--invariants', action="store", nargs="+", help='space separated list of invariant \
      types. E.g cc tri deg mad eig ss1 for clustering coefficient, triangle count, degree, maximum \
      average degree, eigen-pairs & scan-1 statistic')
  result = parser.parse_args()

  assert result.invariants, "Some invariants must be computed"

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

  ''' **IMPORTANT: THIS IS HOW TO BUILD THE URL** '''
  result.url = result.url if result.url.endswith('/') else result.url + '/' #
  call_url = result.url + result.email + "/" + result.input_format + "/" + "/".join(result.invariants)

  try:
    req = urllib2.Request (call_url, tmpfile.read())
    print "Calling url ..."
    response = urllib2.urlopen(req)

  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error:", e
    sys.exit(0)

  print "\n====> " + response.read()

if __name__ == "__main__":
  main()
