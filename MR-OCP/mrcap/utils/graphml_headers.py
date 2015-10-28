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

#graphml_headers.py
# Created by Disa Mhembere on 2015-09-10.
# Email: disa@jhu.edu

import argparse
import re

class Container(object):
  """ This is a shell for an igraph cotainer object """
  def __init__(self, attrs=[]):
    self.attrs = attrs

  def attribute_names(self,):
    return self.attrs

  def __repr__(self):
    return "{0}".format(self.attrs)

class VertexContainer(Container):
  pass

class EdgeContainer(Container):
  pass

class GraphContainer(object):
  """ This is a shell for an igraph graph object """
  
  def __init__(self, g_attrs={}, v_attrs=VertexContainer(), e_attrs=EdgeContainer()):
    self.attrs = g_attrs
    self.vs = v_attrs
    self.es = e_attrs

  def __getitem__(self, var):
    return self.attrs.__getitem__(var)

  def vcount(self,):
    return self.attrs["vcount"]

  def ecount(self,):
    return self.attrs["ecount"]

  def attributes(self,):
    return self.attrs.keys()

  def __repr__(self,):
    return "\nGraph Container:\nGraph: {0}\nVertex: {1}\nEdges: {2}".\
        format(self.attrs, self.vs, self.es)

def read_graphml_headers(fn):
  f = open(fn, "rb")

  g_attrs = {}
  e_attrs = []
  v_attrs = []
  
  g_key_patt = re.compile("g_\w*") 

  while True:
    line = f.readline().strip()
    if line.startswith("<node"):
      break # No more metadata
    elif line.startswith("<key"):
      attr = line.split("\"")[1]
      if attr.startswith("v_"):
          v_attrs.append(attr[2:])
      elif attr.startswith("e_"):
          e_attrs.append(attr[2:])
    elif line.startswith("<data"): # These are graph attributes
      lsplit = line.split(">") 
      m = re.search(g_key_patt, lsplit[0])
      key = m.string[m.span()[0]:m.span()[1]][2:] # skip the `g_`
      g_attrs[key] = lsplit[1].split("<")[0]

  # Fail on graphs without these attrs
  if not g_attrs.has_key("vcount") and not g_attrs.has_key("ecount"):
    raise AttributeError("Expected graph attribures vcount & ecount")

  return GraphContainer(g_attrs, VertexContainer(v_attrs), EdgeContainer(e_attrs))

def test():
  parser = argparse.ArgumentParser(description="Partial read of a graphml graph for attrs")
  parser.add_argument("graphfn", action="store", help="The graph filename")
  result = parser.parse_args()

  g = read_graphml_headers(result.graphfn)
  print g

if __name__ == "__main__":
  test()
