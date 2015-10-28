
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
import urllib2
import argparse
import sys
import os
import scipy.io as sio

import zipfile
import tempfile

import webbrowser

''' RESTful API '''

def main():

  parser = argparse.ArgumentParser(description='Upload and convert a graph from \
      graphml,ncol,edgelist,lgl,pajek,graphdb,numpy,mat to \
      graphml,ncol,edgelist,lgl,pajek,dot,gml,leda object. Base url -> \
      http://openconnecto.me/graph-services/convert')

  parser.add_argument('url', action="store", help='url must be in the form \
      http://openconnecto.me/graph-services/convert/.')

  parser.add_argument('fileToConvert', action="store", help="The file you want to convert.\
      Can be a single graph or a zip file with multiple graphs. Zip graphs and not folders \
      or failure will occur!")
  parser.add_argument("email", action="store", help="Your email address")
  parser.add_argument("-i", "--input_format",  action="store", help="Input format of the grpah")
  parser.add_argument("-o", "--output_format",  action="store", nargs="+", \
      help="Output format of the grpah e.g graphml,ncol,edgelist,lgl,pajek,dot,gml,leda")
  parser.add_argument('-l', '--link', action="store_true", help="Use this flag if you want to \
      ONLY receive the link to your result. If you request multiple output formats this will be a directory.")

  result = parser.parse_args()

  if not result.output_format:
    print "You must provide an output format!"
    exit(-1)
  if not (os.path.exists(result.fileToConvert)):
    print "Invalid file name. Check the filename: " + result.fileToConvert
    exit(-1)
  else:
    print "Loading file into memory.."

  tmpfile = tempfile.NamedTemporaryFile()
  zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)

  zfile.write(result.fileToConvert)
  zfile.close()

  tmpfile.flush()
  tmpfile.seek(0)

  result.url = result.url if result.url.endswith('/') else result.url + '/' #
  call_url = result.url + result.email + "/" + result.input_format + "/" + \
                        ",".join(result.output_format)

  try:
    if result.link:
      req = urllib2.Request(call_url+"/l", tmpfile.read()) # Just return link
    else:
      req = urllib2.Request(call_url, tmpfile.read())

    response = urllib2.urlopen(req)

  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error:", e
    sys.exit(0)

  print "\n====> " + response.read()

if __name__ == "__main__":
  main()
