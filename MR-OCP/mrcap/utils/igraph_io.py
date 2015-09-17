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

# igraph_io.py
# Created by Disa Mhembere on 2014-07-14.
# Email: disa@jhu.edu

from time import time
import zipfile
import tempfile
import os
from igraph import read as igraph_read
from graphml_headers import read_graphml_headers

def write_mm(g, fn):
  """
  Write to MM format given a graph
  @param g: An igraph graph
  @param fn: The output filename
  """
  f = open(fn, "w")
  f.write("%d %d %d\n" % (g.vcount(), g.vcount(), g.ecount()))

  if g.is_weighted():
    for e in g.es():
      f.write("%d %d %.4f\n" % (e.source, e.target, e["weight"]))
  else:
    for e in g.es():
      f.write("%d %d 1\n" % (e.source, e.target))

  f.close()

def unzip_file(fn):
  start = time()
  f = zipfile.ZipFile(fn, "r", allowZip64=True)
  tmpfile = tempfile.NamedTemporaryFile("w", delete=False, dir="/data/pytmp")
  tmpfile.write(f.read(f.namelist()[0])) # read into mem
  tmpfile.close()
  print "Unzip of %s took %f sec ..." % (fn, (time()-start))
  return tmpfile.name

def untar_file(fn):
  print "Uzing tar!"
  import tarfile as tar
  start = time()
  assert tar.is_tarfile(fn), "Not a tarfile"
  f = tar.open(fn, mode="r")
  assert len(f.getnames()) == 1, "Cannot uncompress multiple tars"
  
  tfn = f.getnames()[0]
  f.extract(tfn, path=tempfile.gettempdir())
  f.close()
  print "Untar of %s took %f sec ..." % (fn, (time()-start))
  return os.path.join(tempfile.gettempdir(), tfn)

def read_arbitrary(fn, informat="graphml", headers_only=False):
  tmpfile_name = ""
  print "Attempting arbirary read of : %s ..." % fn
  do_del = False
  if os.path.splitext(fn)[1] == ".zip":
    fn = unzip_file(fn)
    do_del = True
  elif os.path.splitext(fn)[1] == ".gz":
    fn = untar_file(fn)
    do_del = True

  start = time()
  try:
    if (headers_only):
      g = read_graphml_headers(fn)
      print "   Fast read took %.3f sec .." % ((time()-start))
    else: assert 0
  except:
    g = igraph_read(fn, format=informat)
    print "   Read took %.3f sec ..." % ((time()-start))
  finally:
    if do_del: 
      print "Deleting temp %s" % fn
      os.remove(fn)
  return g
