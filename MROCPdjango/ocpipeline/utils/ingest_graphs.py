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

# ingest_graphs.py
# Created by Disa Mhembere on 2014-02-10.
# Email: disa@jhu.edu

from paths import include
include()

import argparse
import os
from glob import glob
import MySQLdb
from contextlib import closing
import igraph
import tempfile
import zipfile
from time import time
from ocpipeline.settings_secret import DATABASES as db_args

def ingest(genera, tb_name, base_dir=None, files=None):
  if files:
    print "Running specific file(s) ..."
    assert len(genera) < 2, "Can only specify single genus as '-g [--genera] arg. You provided %s'" % genera 
    _ingest_files(files, genera[0])
  
  else:
    print "Running entire dataset ..."
    for genus in genera:
      graphs = glob(os.path.join(base_dir, genus, "*")) # Get all graphs in dir
      _ingest_files(graphs, genus, tb_name)

  print "Checking for stale entries ..."
  clean_stale_graphs(tb_name)

  print "\nMission complete ..."

def _ingest_files(fns, genus, tb_name):

  print "Connecting to database %s ..." % db_args["default"]["NAME"]
  db = MySQLdb.connect(host=db_args["default"]["HOST"], user=db_args["default"]["USER"], 
     passwd=db_args["default"]["PASSWORD"], db=db_args["default"]["NAME"])
  db.autocommit(True)

  with closing(db.cursor()) as cursor:
    cursor.connection.autocommit(True)

    for graph_fn in fns:
      print "Processing %s ..." % graph_fn
      mtime = os.stat(graph_fn).st_mtime # get modification time
      g_changed = True
      # In DB and modified
      test_qry ="select g.mtime from %s.%s as g where g.filepath = \"%s\";" % (db_args["default"]["NAME"], tb_name, graph_fn)

      if cursor.execute(test_qry): # Means graph already in DB
        if cursor.fetchall()[0][0] == os.stat(graph_fn).st_mtime: # Means graphs hasn't changed since ingest
          g_changed = False
          print "Ignoring %s ..." % graph_fn
        else:
          cursor.execute("delete from %s.%s where filepath = \"%s\";" % (db_args["default"]["NAME"], tb_name, graph_fn))
          print "  ===> Updating %s ..." % graph_fn

      if g_changed: # Means graph has changed since ingest OR was never in DB to start with
        # Collect all the attributes etc ..
        try:
          g = igraph.read(graph_fn, format="graphml")
        except:
          "Attempting unzip and read ..."
          start = time()
          f = zipfile.ZipFile(graph_fn, "r")
          tmpfile = tempfile.NamedTemporaryFile("w", delete=False)
          tmpfile.write(f.read(f.namelist()[0])) # read into mem
          tmpfile.close()
          g = igraph.read(tmpfile.name, format="graphml")
          os.remove(tmpfile.name)
          print "  Read zip %s ..." % graph_fn

        vertex_attrs = g.vs.attribute_names()
        edge_attrs = g.es.attribute_names()
        graph_attrs = g.attributes()
        vcount = g.vcount()
        ecount = g.ecount()
        # Give some default values if none exist
        if "sensor" in graph_attrs: sensor = g["sensor"]
        else: sensor = "N/A"
        if "source" in graph_attrs: source = g["source"]
        else: source = "N/A"
        if "region" in graph_attrs: region = g["region"]
        else: region = "N/A"
        if "project" in graph_attrs: project = g["project"]
        else: project = "N/A"

        url = "http://openconnecto.me/data/public/graphs/"+("/".join(graph_fn.replace("\\", "/").split('/')[-2:]))
       
        # This statement puts each graph into the DB
        qry_stmt = "insert into %s.%s values (\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%f,\"%s\");" \
             % (db_args["default"]["NAME"], tb_name, os.path.abspath(graph_fn), genus, region, project, 
                 int(vcount), int(ecount), str(graph_attrs)[1:-1].replace("'",""), 
                 str(vertex_attrs)[1:-1].replace("'",""),
                 str(edge_attrs)[1:-1].replace("'",""), sensor, source, mtime, url)

        cursor.execute(qry_stmt)

def clean_stale_graphs(tb_name):
  """ If we have any graphs that have been deleted we should also clean them from db """

  print "Connecting to database %s ..." % db_args["default"]["NAME"]
  db = MySQLdb.connect(host=db_args["default"]["HOST"], user=db_args["default"]["USER"], 
     passwd=db_args["default"]["PASSWORD"], db=db_args["default"]["NAME"])
  db.autocommit(True)

  with closing(db.cursor()) as cursor:
    cursor.connection.autocommit(True)
    cursor.execute("select filepath from %s.%s;" % (db_args["default"]["NAME"], tb_name))

    all_files = cursor.fetchall()

    if all_files:
      for fn in all_files:
        if not os.path.exists(fn[0]):
          print "  ===> Deleting entry with filepath %s from database ..." % fn[0]
          cursor.execute("delete from %s.%s where filepath = \"%s\"" % (db_args["default"]["NAME"], tb_name, fn[0]))

def main():
  parser = argparse.ArgumentParser(description="Ingest the graphs within the dirs specified by 'genera' list.")
  parser.add_argument("base_dir", action="store", help="directory where genus folders are stored")
  parser.add_argument("-g", "--genera", action="store", default=["human", "macaque", "cat", "fly",
            "mouse", "rat", "worm" ] ,nargs="*", help="Can be multiple - just separate with spaces.\
            The directories where to look for file(s) default is : human macaque cat fly mouse rat worm")
  parser.add_argument("-f", "--file_names", action="store", default=None, nargs="+", help="If you only want to ingest \
            specific files only use this")
  parser.add_argument("-t", "--table_name", action="store", default="ocpipeline_graphdownloadmodel", help="Table name in db")
  result = parser.parse_args()
  
  print "Ingesting graph(s) ..."
  ingest(result.genera, result.table_name, result.base_dir, result.file_names, result.project)

if __name__ == "__main__":
  main()
