#!/usr/bin/python

# test_mrocp_inv.py
# Created by Disa Mhembere on 2013-12-31.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

import argparse
from computation.utils.loadAdjMatrix import loadAnyMat
from computation.composite.invariants import compute
from time import time

def main():
  parser = argparse.ArgumentParser(description="Run MROCP invariants individually for timing purposes")

  parser.add_argument("gfn", action="store", help="The name of the graph on disk")
  result = parser.parse_args()

  g = loadAnyMat(result.gfn)

  begin = time()

  # TODO optimize invariants

  # Deg
  print "Individual run ...\n Processing Degree vector ..."
  b = time()
  compute({"deg":True, "G":g, "graph_fn":result.gfn}, save=False)
  print "Time for degree vector = %.4f"% (time()-b)

  # SS
  print "Processing Scan Statistic ..."
  b = time()
  compute({"ss1":True, "G":g, "graph_fn":result.gfn}, save=False)
  print "Time for scan 1 vector = %.4f"% (time()-b)

  # CC
  print "Processing Clustering Coefficient (Transitivity)"
  b = time()
  compute({"cc":True, "G":g, "graph_fn":result.gfn}, save=False)
  print "Time for Clustering Coefficient vector = %.4f"% (time()-b)

  # TRI
  b = time()
  compute({"tri":True, "G":g, "graph_fn":result.gfn}, save=False)
  print "Time for triangle vector = %.4f" % (time()-b)

  print "Total time for non-daisy-chained invariant = %.4f" % (time()-begin) # minus all the populate_invariants

  print "\n*** Daisy-chain run ... ***\n"

  begin = time()
  compute({"deg":True, "ss1":True, "cc":True, "tri":True, "G":g, "graph_fn":result.gfn}, save=False)
  print "Total time for daisy-chained invariant = %.4f" % (time()-begin) # minus all the populate_invariants

if __name__ == "__main__":
  main()