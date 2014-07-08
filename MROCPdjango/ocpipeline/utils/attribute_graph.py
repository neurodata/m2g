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
from subprocess import call
import os
from time import time
import igraph
from glob import glob

def attribute_graph(graph_fns, attrs, overwrite):
  for graph_fn in graph_fns:
    start = time()
    print "Attempting unzip ..."
    f = zipfile.ZipFile(graph_fn, "r")
    print "Attempting read and split ..."
    uncompressed_fn = f.namelist()[0]
    text = f.read(uncompressed_fn).splitlines()
    f.close()

    print "Inserting headers ... "
    for key in attrs: 
      text.insert(6, '  <key id="g_%s" for="graph" attr.name="%s" attr.type="string"/>\n' % (key, key))

    # Insert values
    for key in attrs: 
      text.insert( 31 + len(attrs), '    <data key="g_%s">%s</data>\n' % (key, attrs[key]))

    if overwrite:
      out_fn = graph_fn
    else:
       out_fn = os.path.splitext(graph_fn)[0] + "_attr.zip" 

    print "Writing %s back to disk ...." % out_fn
    
    tmpfile = tempfile.NamedTemporaryFile("w", delete=False)
    tmpfile.write("\n".join(text)) # read into mem
    tmpfile.close()

    rename =  os.path.join(os.path.dirname(tmpfile.name), os.path.basename(uncompressed_fn))
    
    call(["mv", tmpfile.name, rename])
    call(["zip", "-jv", out_fn, rename])
    print "Deleting %s ..." % rename
    os.remove(rename)

    #with zipfile.ZipFile(out_fn, "w", allowZip64=True) as graph_zip:
    #  graph_zip.writestr(f.namelist()[0], "\n".join(text)) 

    #graph_zip.close()

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
