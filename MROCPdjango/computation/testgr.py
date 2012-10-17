import networkx as nx
import numpy as np

from utilhltcoe import evaluate_graph

def createGraph():
  
  numNodes  = 10
  nodeProb = 0.65
  randGr = nx.binomial_graph(numNodes,nodeProb,directed=False)
  
  adjMat = [ [ 0 for i in range(numNodes) ] for j in range(numNodes) ]
  
  for row in range (len(randGr.adj.items())):
    for ind in ((randGr.adj.items()[row])[1]).keys():
      adjMat[row][ind] = 1
      

  print "Sanity Check \n============================="
  print "Size/Number of edges =", randGr.number_of_edges()

  inv = evaluate_graph(randGr, -1)
  printUTIL(inv)
  writeUTIL(inv)
  
  #print "My calcs"
def printUTIL(inv):
  print "\n\n utilhltcoe.py \n==========================="
  print "Size/Number of edges =", inv[0]
  print "Max degree =", inv[1]
  print "MAD Eigenvalue=", inv[2]
  print "Scan Stat1=", inv[3]
  print "Num triangles", inv[4]
  print "Clustering Coeff", inv [5]
  print "Average Path Length", inv[6]
  print "Greedy MAD", inv[7]
  
def writeUTIL(inv):
  
  f = open("benchmark.graph",'w')
  
  f.write("utilhltcoe.py \n===========================\n")
  f.write("\nSize/Number of edges = "+str(inv[0])+"\nMax degree = "+str(inv[1]) )
  f.write("\nMAD Eigenvalue = "+str(inv[2])+"\nScan Stat1 = "+str(inv[3]))
  f.write("\nScan Stat1 = "+str(inv[3]) + "\nNum triangles = "+str(inv[4]))
  f.write("\nClustering Coeff = "+str(inv[5])+"\nAverage Path Length = "+str(inv[6]))
  f.write("\nGreedy MAD= "+str(inv[7]))
  
  f.close()

if __name__ == '__main__':
  createGraph()
  