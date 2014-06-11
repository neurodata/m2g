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

# attribute_graph.py
# Created by Disa Mhembere on 2014-05-29.
# Email: disa@jhu.edu

import argparse
import tempfile
import zipfile
import multiprocessing
import os
from time import time
import igraph
from glob import glob

def attribute_graph(graph_fns, attrs, overwrite):
  for graph_fn in graph_fns:
    start = time()
    try:
      g = igraph.read(graph_fn, format="graphml")
      print "Read %s as graphml format ..." % graph_fn
      
    except:
      "Attempting unzip and read ..."
      f = zipfile.ZipFile(graph_fn, "r")
      tmpfile = tempfile.NamedTemporaryFile("w", delete=False)
      tmpfile.write(f.read(f.namelist()[0])) # read into mem
      tmpfile.close()
      g = igraph.read(tmpfile.name, format="graphml")
      os.remove(tmpfile.name)
      print "  Read zip %s ..." % graph_fn  

    for key in attrs: 
      g[key] = attrs[key]
    
    # Case I have a zip file
    if os.path.splitext(graph_fn)[1] ==  ".zip":
      tmpfile = tempfile.NamedTemporaryFile("w", delete=False)
      print "Writing tempfile %s ..." % tmpfile.name
      g.write_graphml(tmpfile.name)
    
      if overwrite:
        out_fn = graph_fn
      else:
         out_fn = os.path.splitext(graph_fn)[0] + "_attr.zip" 

      print "Writing %s back to disk ...." % out_fn
      with zipfile.ZipFile(out_fn, "w") as graph_zip:
        graph_zip.write(tmpfile.name, f.namelist()[0]) # TODO: verify 2nd param

      f.close()

      tmpfile.close()
      os.remove(tmpfile.name)

    # Not a zipfile
    else:
      _format = os.path.splitext(graph_fn)[1][1:] 

      if overwrite:
        out_fn = graph_fn
      else:
         out_fn = os.path.splitext(graph_fn)[0] + "_attr." + _format 
      try:
        print "Writing %s back to disk ..." % out_fn
        g.write(out_fn, format=_format)

      except:
        sys.stderr.write("Unknown format %s ...\n" % _format )

    print "Time taken = %.3f sec" % (time()-start)

def main():
  parser = argparse.ArgumentParser(description="Add attributes a graphml object and write it")
  parser.add_argument("-g", "--graph_fns", action="store", nargs="+", help="graph filename(s)")
  parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite existing?")
  parser.add_argument("-a", "--graph_attrs", nargs="+", default={}, action="store", help="Graph attributes to add")
  result = parser.parse_args()

  # Parse dict
  if result.graph_attrs:
    graph_attrs = {}
    for item in result.graph_attrs:
      sp = item.split(":")
      graph_attrs[sp[0].strip()] = sp[1].strip()
    result.graph_attrs = graph_attrs

  if os.path.isdir(result.graph_fns[0]):
    attribute_graph(glob(os.path.join(result.graph_fns[0], "*")), result.graph_attrs, result.overwrite)
  else:
    attribute_graph(map(os.path.abspath, result.graph_fns), result.graph_attrs, result.overwrite)

if __name__ == "__main__":
  main()
