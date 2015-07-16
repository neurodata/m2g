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

# ocp_mri_upload.py
# Created by Greg Kiar on 2015-07-01.
# Email: gkiar@jhu.edu

import numpy as np
import urllib, urllib2
import cStringIO
import sys
import tempfile
import zlib

from argparse import ArgumentParser

def nifti_upload(infname, server, token, channel):
  from nibabel import load
  from numpy import array

  print "Parsing nifti file..."
  nifti_img = load(infname)
  nifti_data = np.transpose(np.array(nifti_img.get_data()))

  # GKTODO use actual command line parameters
  # build a URL
  #url = "{}/ocp/ocpca/{}/{}/npz/".format('http://rio.cs.jhu.edu',token,channel)
  url = "{}/ocp/ocpca/{}/{}/npz/".format(server,token,channel)

  # add dimensional arguments
  url += "{}/{},{}/{},{}/{},{}/".format(0,0,182,0,218,0,182)

  # reshape the nifti data to include a channel dimension
  nifti_data = np.uint16(nifti_data.reshape([1]+list(nifti_data.shape)))
  
  # encode numpy pick
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, nifti_data )
  cdz = zlib.compress (fileobj.getvalue())

  # Upload to server
  print "Uploading data..."
  try:
    # Build the post request
    req = urllib2.Request(url, cdz)
    response = urllib2.urlopen(req)
    the_page = response.read()
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e)
    sys.exit(-1)


  
def swc_upload(infname, token):
  from contextlib import closing

  # GKTODO use actual command line parameters
  # build a URL
  url = "{}/ocpca/{}/{}/swc/".format('http://rio.cs.jhu.edu:8000','mniatlas','fibers')

  with closing ( open(infname) ) as ifile:

    # Upload to server
    try:
      # Build the post request
      req = urllib2.Request(url, ifile.read())
      response = urllib2.urlopen(req)
      the_page = response.read()
    except urllib2.URLError, e:
      print "Failed %s.  Exception %s." % (url,e)
      sys.exit(-1)

  return

  print "Parsing skeleton file..."
  with closing(open(infname, mode="rb")) as fiber_f:
    fdata = fiber_f.read()
  lines = fdata.split("\n")
  count = 0
  for line in lines: #GK TODO: speed up; isn't huge deal because headers are short
    if line[0] == "#":
      count += 1
    else:
      break #this assumes no comments after header

  head = lines[:count]
  skel = lines[count:]

  #Displaying shit to happy users :)
  print "Header:"
  for elem in head:
    print elem
  if len(skel) <= 2:
    print "\nData: \n", skel[0], "\n..."
  else:
    print "\nData: \n", skel[0], "\n", skel[1], "\n..."


def main():
  parser = ArgumentParser(description="Allows users to upload nifti images to OCP")
  parser.add_argument("server", action="store", help="server http://...")
  parser.add_argument("token", action="store", help="token for the project which you're uploading to")
  parser.add_argument("channel", action="store", help="channel to which you're uploading")
  parser.add_argument("data", action="store", help="Data which is to be uploaded")
  parser.add_argument("--formats", "-f", action="store", default="nifti", help="format: nifti, swc")
  result = parser.parse_args()
  
  if result.formats == "nifti":
    nifti_upload(result.data, result.server, result.token, result.channel)
  elif result.formats == "swc":
    swc_upload(result.data, result.token)
  else:
    print 'Error: unknown format'
    return -1

if __name__ == "__main__":
  main()
