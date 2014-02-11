#!/usr/bin/python

# ingest_graphs.py
# Created by Disa Mhembere on 2014-02-10.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

import argparse
import MySQLdb
from ocpipeline.settings_secret import DATABASES as db
import igraph
from glob import glob
import os
from contextlib import closing

def ingest(base_dir):
  genera = ["human", "macaque", "cat", "fly",
            "mouse", "rat", "worm" ]
  
  for genus in genera:
    graphs = glob(os.path.join(base_dir,"*")) # Get all graphs in dir

    for graph_fn in graphs:
      g = igraph.read(graph_fn, format="graphml")
      vertex_attrs = g.vs.attribute_names()
      edge_attrs = g.es.attribute_names()
      graph_attrs = g.attributes()
      vcount = g.vcount()
      ecount = e.ecount()
      
      if "sensor" in graph_attrs: sensor = g["sensor"]
      else: sensor = "NULL"
      if "source" in graph_attrs: source = g["source"]
      else: source = "NULL"
      if "region" in graph_attrs: region = g["region"]
      else: region = "NULL"
      
      print "Connecting to database %s ..." % db["default"]["NAME"]
      db = MySQLdb.connect(host=db["default"]["HOST"], user=db["default"]["USER"], 
         passwd=db["default"]["PASSWORD"], db=db["default"]["NAME"])
      db.autocommit(True)

      with closing(db.cursor()) as cursor:
        cursor.connection.autocommit(True)
        cursor.execute("insert into %s.graphs VALUES (%s,%s,%s,%s,%d,%d,%s,%s,%s,%s,%s);" 
           % (db["default"]["NAME"], graph_fn, genus, region, vcount, 
             ecount, str(graph_attrs), str(vertex_attrs), str(edge_attrs), sensor, source)
           )

def main():
  parser = argparse.ArgumentParser(description="Ingest all the graphs withing the dirs specified by 'genera' list.")
  parser.add_argument("base_dir", action="store", help="directory where genus folders are stored")
  result = parser.parse_args()

if __name__ == "__main__":
  main()
