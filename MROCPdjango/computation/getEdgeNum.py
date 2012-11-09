import scipy.io as sio
from glob import glob
import numpy as np
import os
import argparse
from getBaseName import getBaseName

#import json

def getEdgeNum(graphDir, toDir):
  
  edgeNum = {}
  
  for f in glob(os.path.join(graphDir,'*')):
    edgeNum [getBaseName(f)] = (sio.loadmat(f)['fibergraph']).nnz 
    #json.dumps(edgeNum)
  
  edgeArr = np.array(edgeNum.values())
  
  if not os.path.exists(toDir):
    os.makedirs(toDir)
  
  np.save("numEdges.npy", edgeArr)
  
def main():
    
    parser = argparse.ArgumentParser(description='Get the number of edges per graph')
    parser.add_argument('graphDir', action='store',help='Full dir name of directory with graphs (.mat)')
    parser.add_argument('toDir', action='store', help='Full path of directory where you want result .npy array to go')
    
    result = parser.parse_args()
    getEdgeNum(result.graphDir,result.toDir)

if __name__ == '__main__':
  main()
 
  