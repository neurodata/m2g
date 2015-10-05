
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

import zipfile
import tempfile

def main():
  parser = argparse.ArgumentParser(description="Build a subjects graph given data. \
      Base url -> http://openconnecto.me/graph-services/buildgraph")
  parser.add_argument("url", action="store", help="url must have NO SPACES & \
      must be in the form  http://openconnecto.me/graph-services/buildgraph/\
      {projectName}/{site}/{subject}/{session}/{scanID}/{s|b}, where s= smallgraph OR b = biggraph")
  parser.add_argument("fiberfile", action="store", help="MRI studio fiber file")
  parser.add_argument("email", action="store", help="your email address")
  parser.add_argument("-i", "--invariants", action="store", nargs="*", \
      help="OPTIONAL: a list of invariants types. E.g cc tri deg mad for \
      clustering coefficient, triangle count, degree & maximum average degree")

  parser.add_argument("-a","--atlas", action="store", help="NIFTI format atlas")

  result = parser.parse_args()

  result.url = result.url if result.url.endswith("/") else result.url + "/" #

  try:
    # Create a temporary file to store zip contents in memory
    tmpfile = tempfile.NamedTemporaryFile()
    zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)

    zfile.write(result.fiberfile)
    if result.atlas:
      zfile.write(result.atlas)

    zfile.close()

    tmpfile.flush()
    tmpfile.seek(0)

#  Testing only: check the contents of a zip file.
    """
    rzfile = zipfile.ZipFile(tmpfile.name, "r", allowZip64=True)
    ret = rzfile.printdir()
    ret = rzfile.testzip()
    ret = rzfile.namelist()
    """

  except:
    print "Check the filenames: fiber:", result.fiberfile
    if (result.atlas):
      print "atlas:", result.atlas

    sys.exit(0)

  try:
    call_url = result.url + result.email + "/" + "/".join(result.invariants)
    print "Calling url: %s" % call_url
    req = urllib2.Request (call_url, tmpfile.read()) # Important to concatenate these in this order
    response = urllib2.urlopen(req)

  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error:", e
    sys.exit(0)

  print "\n====> " + response.read()

if __name__ == "__main__":
  main()
