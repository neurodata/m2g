import scipy.io as sio
import sys
from glob import glob
def graphIsUpperTri():
  
  for gr in glob(sys.argv[1],'*'):
    
    print "Assessing" + gr
    G = sio.loadmat(gr)['fibergraph']
    
    if (G.shape[0] != G.shape[1]):
      print gr + " has unequal rows and columns"
      print gr + " rows = %d and cols = %d" % (G.shape[0], G.shape[1])
  
    for row in range(G.shape[0]):
      for col in range (G.shape[1]):
        if (G[row,col]>0 and (row > col)):
          print "Error row:%d , col:%d > 0" % (row, col)
          
if __name__ == '__main__':
  graphIsUpperTri()