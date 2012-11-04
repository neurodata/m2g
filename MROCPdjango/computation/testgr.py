import networkx as nx
import numpy as np
import scipy.io as sio
from scipy.sparse import *
from scipy import *
import os
import argparse

from goldstd import evaluate_graph
def createGraph(numNodes = 10):
  
  #numNodes = int(NumNodes)
  
  G_fn = "bench_concomp"+str(numNodes)
  nodeProb = 0.4
  randGr = nx.binomial_graph(numNodes,nodeProb,directed=False)
  
  adjMat = [ [ 0 for i in range(numNodes) ] for j in range(numNodes) ]
  
  for row in range (len(randGr.adj.items())):
    for ind in ((randGr.adj.items()[row])[1]).keys():
      adjMat[row][ind] = 1
  
  # Make equivalent csc_matrix
  Gsparse = csc_matrix(adjMat, dtype=float64)
  
  if not os.path.exists(os.path.join("bench",str(numNodes))):
    os.makedirs(os.path.join("bench",str(numNodes)))
  
  sio.savemat(os.path.join("bench",str(numNodes) ,G_fn),{'fibergraph': Gsparse}, appendmat = True)
  
  inv = evaluate_graph(randGr, -1)
  
  printUTIL(inv)
  writeUTIL(inv)
  
def printUTIL(inv):
  print "\n GLOBALS\n==========================="
  print "Size/Number of edges =", inv[0]
  print "Max degree =", inv[1]
  print "MAD Eigenvalue=", inv[2]
  print "Scan Stat1 =", inv[3]
  print "Num triangles =", inv[4]
  print "Clustering Coeff =", inv [5]
  print "Average Path Length =", inv[6]
  print "Degree =", inv[7]
  print "Greedy MAD =", inv[8], "\n"
  
def writeUTIL(inv):  
  
  f = open(os.path.join("bench",str(inv[7]),"bench_concomp.meta."+str(inv[7])),'w')
  f.write("GLOBALS\n===========================\n")
  f.write("\nSize/Number of edges = "+str(inv[0])+"\nMax degree = "+str(inv[1]) )
  f.write("\nMAD Eigenvalue = "+str(inv[2]))
  f.write("\nScan Stat1 = "+str(inv[3]) + "\nNum triangles = "+str(inv[4]))
  f.write("\nClustering Coeff = "+str(inv[5])+"\nAverage Path Length = "+str(inv[6]))
  f.write("\nDegree = "+str(inv[7]) + "\nGreedy MAD= "+str(inv[8]))
  
  f.close()

def main():
    
    parser = argparse.ArgumentParser(description='Calculate true local Scan Statistic and Degree in a graph')
    parser.add_argument('numNodes', type = int, action='store',help='The number of nodes in the graph you want to generate')
    
    result = parser.parse_args()
    
    createGraph(result.numNodes)
    
if __name__ == '__main__':
  main()
  #createGraph(10)
  #createGraph(50)
  #createGraph(1000)