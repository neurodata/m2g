import networkx as nx
import numpy as np
import scipy.io as sio
from scipy.sparse import *
from scipy import *
import os
import argparse

from goldstd import evaluate_graph
def createGraph(numNodes, nodeProb):
  """ Create a graph and compute and save """

  print "Creating random graph with node connectivity probability = %f ...." % nodeProb 
  
  G_fn = "bench_concomp"+str(numNodes)
  randGr = nx.binomial_graph(numNodes, nodeProb, directed=False)
  adjMat = [ [ 0 for i in range(numNodes) ] for j in range(numNodes) ]
  
  for row in range (len(randGr.adj.items())):
    for ind in ((randGr.adj.items()[row])[1]).keys():
      adjMat[row][ind] = 1
  
  # Make equivalent csc_matrix
  Gsparse = csc_matrix(adjMat, dtype=float64)
  gdir = os.path.join("bench",str(numNodes))

  if not os.path.exists(gdir):
    os.makedirs(gdir)
  sio.savemat(os.path.join(gdir ,G_fn),{"fibergraph": Gsparse}, appendmat = True)
  print "Your graph is saved in %s ...\n" % os.path.abspath(gdir)
  inv = evaluate_graph(randGr, -1)

  printUTIL(inv)
  writeUTIL(inv)

def createER(numNodes, nodeProb):
  """ Create an ER graph, compute invariants from goldstd and write to disk as scipy csc  """
  print "Creating ER graph with node connectivity probability = %f ...." % nodeProb 

  G_fn = "bench_concomp"+str(numNodes) 
  g = nx.erdos_renyi_graph(numNodes, nodeProb, directed=False)
  gs = nx.to_scipy_sparse_matrix(g, format="csc", dtype="float32")

  gdir = os.path.join("bench",str(numNodes))

  if not os.path.exists(gdir):
    os.makedirs(gdir)
  sio.savemat(os.path.join(gdir ,G_fn),{"fibergraph": Gsparse}, appendmat = True)
  print "Your graph is saved in %s ...\n" % os.path.abspath(gdir)

  inv = evaluate_graph(g, -1)

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
  
  f = open(os.path.join("bench",str(inv[7]),"bench_concomp.meta."+str(inv[7])),"w")
  f.write("GLOBALS\n===========================\n")
  f.write("\nSize/Number of edges = "+str(inv[0])+"\nMax degree = "+str(inv[1]) )
  f.write("\nMAD Eigenvalue = "+str(inv[2]))
  f.write("\nScan Stat1 = "+str(inv[3]) + "\nNum triangles = "+str(inv[4]))
  f.write("\nClustering Coeff = "+str(inv[5])+"\nAverage Path Length = "+str(inv[6]))
  f.write("\nDegree = "+str(inv[7]) + "\nGreedy MAD= "+str(inv[8]))
  
  f.close()

def main():
    
    parser = argparse.ArgumentParser(description="Generate a graph that is connected")
    parser.add_argument("numNodes", type=int, action="store",help="The number of nodes in the graph you want to generate")
    parser.add_argument("-p", "--nodeProb", type=float, default=0.3, action="store",help="The probability of connectivity")
    parser.add_argument("-t", "--gtype", default="rand", action="store",help="The type of graph to make. Options: rand, er ")
    
    result = parser.parse_args()
    
    # As more types are added this will grow. Use in place of if ... else / case
    func_dict = {
        "rand":createGraph, "er":createER
        }
    
    # Pick which function to use
    func = func_dict[result.gtype.lower().strip()]

    func(result.numNodes, result.nodeProb)
    
if __name__ == "__main__":
  main()
