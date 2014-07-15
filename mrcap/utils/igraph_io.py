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

  for e in g.es():
    f.write("%d %d %.4f\n" % (e.source, e.target, e["weight"]))

  f.close()

def read_arbitrary(fn, informat="graphml"):
  try:
    g = igraph_read(fn, format=informat)
  except:
    start = time()
    f = zipfile.ZipFile(fn, "r", allowZip64=True)
    tmpfile = tempfile.NamedTemporaryFile("w", delete=False)
    tmpfile.write(f.read(f.namelist()[0])) # read into mem
    tmpfile.close()
    g = igraph_read(tmpfile.name, format=informat)
    os.remove(tmpfile.name)
    print "  Read zip %s in %f sec ..." % (fn, (time()-start))
  
  return g
