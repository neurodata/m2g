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


def read_arbitrary(fn, informat="graphml"):
  tmpfile_name = ""
  print "Attempting igraph arbirary read of : %s ..." % fn
  if os.path.splitext(fn)[1] == ".zip":
    try:
      tmpfile_name = unzip_file(fn)
      start = time()
      g = igraph_read(tmpfile_name, format=informat)
      print "  Read took %f sec ..." % ((time()-start))
    except:
      g = igraph_read(fn, format=informat)
    finally:
      print "Deleting temp %s" % tmpfile_name
      os.remove(tmpfile_name)
  else:
    try:
      g = igraph_read(fn, format=informat)
    except:
      tmpfile_name = unzip_file(fn)
      start = time()
      g = igraph_read(tmpfile_name, format=informat)
      print "  Read took %f sec ..." % ((time()-start))
    finally:
      if os.path.exists(tmpfile_name):
        print "Deleting temp %s" % tmpfile_name
        os.remove(tmpfile_name)
  return g
