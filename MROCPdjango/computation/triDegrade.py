# Use for test graphs only

import os
import sys
from triCount import eignTriangleLocal
from unittesting import proximityAssertion
import scipy.io as sio
import argparse
import numpy as np
import matplotlib.pyplot as plt

def triangleDegrade(G_fn, dataDir):
  if not os.path.exists(dataDir):
    try:
      os.makedirs(dataDir)
    except:
      print "Absolute file path failed: %s" % dataDir
      
    try:
      os.makedirs(os.path.abspath(dataDir))
    except:
      print "Relative file path creation failed: %s" % dataDir
      sys.exit(-1)
  
  try:
    G = sio.loadmat(G_fn)['fibergraph']
  except:
    print "%s File not found" % G_fn
    sys.exit(-1)
  
  numNodes = G.shape[0]
  numEdges = G.nnz
  
  maxEigs = numNodes - 2
  x = range(1,10)
  x.reverse()
  numEigsArray =  np.append(maxEigs/np.array(range(1,30)),x)
  
  percDiffArray = []
  timeArray = []
  for k in numEigsArray:
    tri_fn, tm = eignTriangleLocal(G_fn, G , lcc_fn = None, roiRootName = None, triDir = dataDir, k = k, degradeTest = True)
    timeArray.append(tm)
    percDiffArray.append(testTriangles( dataDir, k, tri_fn, numNodes, 0.1))

  
  
  np.save("bench/3000/percDiffArray.npy", np.array(percDiffArray))
  np.save("bench/3000/timeArray.npy", np.array(timeArray))
  
  print "***Triangle eignvalue number degradation complete..."
  graphDegrade(percDiffArray, timeArray, dataDir, numEigsArray, numNodes, numEdges)



def testTriangles(dataDir, numEigsArray, tri_fn, numNodes, tol = 0.1):
   percOffBy = proximityAssertion(np.load(tri_fn), np.load(os.path.join("bench",str(numNodes),"triArr.npy")), tol, "Triangle count" )
   print "==========================================================================="
   return percOffBy

def graphDegrade(percDiffArray, timeArray, toDir, numEigsArray, numNodes, numEdges):
  if not os.path.exists(toDir):
    os.makedirs(toDir)
    
  ''' % difference & time '''
  plt.figure(1)
  #plt.subplot(131)
  p1, = plt.plot(numEigsArray,percDiffArray ,'-b')
  p2, =plt.plot(numEigsArray, timeArray ,'-r')
  
  #plt.text(600, 7, 'Nodes: '+ str(numNodes))
  #plt.text(600, 6, 'Edges: '+ str(numEdges))
  plt.legend([p1,p2], ['% Difference', 'Time taken'])
  plt.title('Num eigenvalues VS Time & Accuracy')  
  plt.ylabel('Time taken (s) & Global percent difference')
  plt.xlabel('Number of Eigenvalues computed')
  #plt.show()
  plt.savefig(os.path.join(toDir, "degradeTimeAndPercDiff"+str(numNodes)+".png"))

  ''' % Diff alone '''
  plt.figure(2)
  #plt.subplot(132)
  p1, = plt.plot(numEigsArray[:-1],percDiffArray[:-1] ,'-b')
  #plt.text(600, 0.12, 'Nodes: '+ str(numNodes))
  #plt.text(600, 0.1, 'Edges: '+ str(numEdges))
  #plt.legend([p1], ['% Difference'])
  plt.title('Num eigenvalues VS Accuracy')  
  plt.ylabel('Global percent error')
  plt.xlabel('Number of Eigenvalues computed')
  #plt.show()
  plt.savefig(os.path.join(toDir, "degradePercDiff"+str(numNodes)+".png")) 
  
  ''' Time alone '''
  plt.figure(3)
  #plt.subplot(133)
  p2, =plt.plot(numEigsArray[:-1], timeArray[:-1] ,'-r')
  #plt.text(600, 7, 'Nodes: '+ str(numNodes))
  #plt.text(600, 6, 'Edges: '+ str(numEdges))
  #plt.legend([p2], ['Time taken'])
  plt.title('Num eigenvalues VS Time (s)')  
  plt.ylabel('Time taken')
  plt.xlabel('Number of Eigenvalues computed')
  #plt.show()
  
  plt.savefig(os.path.join(toDir, "degradeTime"+str(numNodes)+".png"))
  
def graphDegrade2(percDiffArray, timeArray, toDir):

  maxEigs = 3000 - 2
  x = range(1,10)
  x.reverse()
  numEigsArray =  np.append(maxEigs/np.array(range(1,30)),x)

  if not os.path.exists(toDir):
    os.makedirs(toDir)

  #import pdb; pdb.set_trace()
    
  ''' % Diff alone '''
  plt.figure(1)
  plt.subplot(121)
  p1, = plt.plot(numEigsArray[1:],percDiffArray[1:] ,'-g')
  #plt.text(600, 0.12, 'Nodes: '+ str(numNodes))
  #plt.text(600, 0.1, 'Edges: '+ str(numEdges))
  #plt.legend([p1], ['% Difference'])
  plt.title('Num eigenvalues VS Accuracy')  
  plt.ylabel('Global percent error')
  plt.xlabel('Number of Eigenvalues computed')
  #plt.show()
  #plt.savefig(os.path.join(toDir, "HBMdegradePercDiff"+".png")) 
  
  ''' Time alone '''
  #plt.figure(2)
  plt.subplot(122)
  p2, =plt.plot(numEigsArray[1:], timeArray[1:],'-g')
  #plt.text(600, 7, 'Nodes: '+ str(numNodes))
  #plt.text(600, 6, 'Edges: '+ str(numEdges))
  #plt.legend([p2], ['Time taken'])
  plt.title('Num eigenvalues VS Time (s)')  
  plt.ylabel('Time taken')
  plt.xlabel('Number of Eigenvalues computed')
  #plt.show()
  
  #plt.savefig(os.path.join(toDir, "HBMdegradeTime"+".png"))
  plt.savefig(os.path.join(toDir, "TotaldegradeTime"+".png"))
  print "****DONE*****"

def main():
  '''
  parser = argparse.ArgumentParser(description='Test triangle counting degradation with number of eigenvalues')
  parser.add_argument('G_fn', action='store',help='Full filename sparse graph (.mat)')
  parser.add_argument('dataDir', action='store', help='Full path of directory where you want .npy arrays resulting file to go')
  
  result = parser.parse_args()
  triangleDegrade( result.G_fn, result.dataDir )
  '''
  import sys
  graphDegrade2(np.load('bench/3000/percDiffArray.npy'), np.load('bench/3000/timeArray.npy'), sys.argv[1])
  
if __name__ == '__main__':
  main()
