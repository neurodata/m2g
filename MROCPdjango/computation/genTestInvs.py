#!/usr/bin/python

# Author: Disa Mhembere
# Determine some graph invariants on big and small test graphs
# Date: 5 Sept 2012


import argparse
import unittesting

# Invariant imports
from getBaseName import getBaseName
from loadAdjMatrix import loadAdjMat
from maxavgdeg import getMaxAveDegree
from scanstat_degr import calcScanStat_Degree
from triCount import eignTriangleLocal
from clustCoeff import calcLocalClustCoeff

###########
# TESTING #
###########

def testing(G_fn, dataDir):
  
  mad = getMaxAveDegree(G_fn)
  ss1_fn, deg_fn, numNodes = calcScanStat_Degree(G_fn)
  tri_fn[0] = eignTriangleLocal(G_fn)
  ccArr_fn = calcLocalClustCoeff(deg_fn, tri_fn, test=True)
  
  testObj = unittesting.test(G_fn, dataDir, numNodes, ss1_fn = ss1_fn, deg_fn = deg_fn, tri_fn = tri_fn, ccArr_fn = ccArr_fn, mad = mad) # Create unittest object
  testObj.testClustCoeff()
  testObj.testDegree()
  testObj.testTriangles()
  testObj.testMAD()
  testObj.testSS1()

#########################  ************** #########################

def main():
  
  parser = argparse.ArgumentParser(description='Runs All invariants of test graphs')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('dataDir', action='store', help='Full path of directory where you want .npy array resulting files to go')
  
  result = parser.parse_args()
  testing(result.G_fn, result.dataDir)

if __name__ == '__main__':
  main()
