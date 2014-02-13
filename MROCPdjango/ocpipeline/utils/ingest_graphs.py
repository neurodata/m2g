#!/usr/bin/python

# ingest_graphs.py
# Created by Disa Mhembere on 2014-02-10.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
import os
from glob import glob
import MySQLdb
from contextlib import closing
import igraph
from ocpipeline.settings_secret import DATABASES as db_args

def ingest(genera, base_dir=None, files=None):
  if files:
    print "Running specific file(s) ..."
    assert len(genera) < 2, "Can only specify single genus as '-g [--genera] arg. You provided %s'" % genera 
    _ingest_files(files, genera[0], db_args)
  
  else:
    print "Running entire dataset ..."
    for genus in genera:
      graphs = glob(os.path.join(base_dir, genus, "*")) # Get all graphs in dir
      _ingest_files(graphs, genus, db_args)

  print "\nMission complete ..."

def _ingest_files(fns, genus, db_args):

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
      test_qry ="select g.mtime from %s.graphs as g where g.filepath = \"%s\";" % (db_args["default"]["NAME"], graph_fn)

      if cursor.execute(test_qry): # Means graph already in DB
        if cursor.fetchall()[0][0] == os.stat(graph_fn).st_mtime:
          g_changed = False
          print "Ignoring %s ..." % graph_fn

      if g_changed:
        g = igraph.read(graph_fn, format="graphml")
        vertex_attrs = g.vs.attribute_names()
        edge_attrs = g.es.attribute_names()
        graph_attrs = g.attributes()
        vcount = g.vcount()
        ecount = g.ecount()
        
        if "sensor" in graph_attrs: sensor = g["sensor"]
        else: sensor = "NULL"
        if "source" in graph_attrs: source = g["source"]
        else: source = "NULL"
        if "region" in graph_attrs: region = g["region"]
        else: region = "NULL"
       
        qry_stmt = "insert into %s.graphs values (\"%s\",\"%s\",\"%s\",%d,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%f);" \
             % (db_args["default"]["NAME"], os.path.abspath(graph_fn), genus, region, int(vcount), 
               int(ecount), str(graph_attrs), str(vertex_attrs), str(edge_attrs), sensor, source, mtime)

        cursor.execute(qry_stmt)

def main():
  parser = argparse.ArgumentParser(description="Ingest the graphs within the dirs specified by 'genera' list.")
  parser.add_argument("base_dir", action="store", help="directory where genus folders are stored")
  parser.add_argument("-g", "--genera", action="store", default=["human", "macaque", "cat", "fly",
            "mouse", "rat", "worm" ] ,nargs="*", help="Can be multiple - just separate with spaces.\
            The directories where to look for file(s) default is : human macaque cat fly mouse rat worm")
  parser.add_argument("-f", "--file_names", action="store", default=None, nargs="+", help="If you only want to ingest \
            specific files only use this")
  
  result = parser.parse_args()
  
  print "Ingesting graph(s) ..."
  ingest(result.genera, result.base_dir, result.file_names)

if __name__ == "__main__":
  main()
