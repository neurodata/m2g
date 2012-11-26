import scipy.io as sio
import sys
from glob import glob
import os

def graphIsUpperTri():
  
  f = open("SymmetryResults.txt",'w')
  for gr in glob(os.path.join(sys.argv[1],'*')):
    
    idStmt = "Assessing " + gr
    print idStmt
    f.write("\n\n" + idStmt + "\n")
    
    G = sio.loadmat(gr)['fibergraph']
    
    if (G.shape[0] != G.shape[1]):
      alertStmt =  gr + " has unequal rows and columns"
      debugStmt = gr + " rows = %d and cols = %d" % (G.shape[0], G.shape[1])
      print alertStmt
      print debugStmt
      f.write(alertStmt+"\n")
      f.write(debugStmt+"\n")
  
    for row in range(G.shape[0]):
      for col in range (G.shape[1]):
        if (G[row,col]>0 and (row > col)):
          fatalStmt =  "Error row:%d , col:%d > 0" % (row, col)
          print fatalStmt
          f.write(fatalStmt +"\n")
    
    finishStmt = gr + " completed"
    print finishStmt
    f.write(finishStmt + "\n")
  
  f.close()
  
if __name__ == '__main__':
  graphIsUpperTri()
