import numpy as np
import os

#Global filenames

class test():
  def __init__(self, G_fn, dataDir, numNodes, ss1_fn = None, deg_fn = None, tri_fn = None, ccArr_fn = None, mad = None):
    self.G_fn = G_fn
    self.numNodes = numNodes
    self.ss1_fn = ss1_fn 
    self.deg_fn = deg_fn
    self.tri_fn = tri_fn
    self.ccArr_fn = ccArr_fn
    self.dataDir = dataDir
    self.mad = mad
    self.benchdir = 'bench'
    
    if not os.path.exists(dataDir):
      os.makedirs(dataDir)
  
  def testMAD(self, limit = 0.1):
    
    benchMAD = float(np.load(os.path.join(self.benchdir, str(self.numNodes),'MAD.npy')))
    var = abs(benchMAD - self.mad)/benchMAD 
    if ( var  > limit):
      print "\n!!!!**** ALERT***** MAD is not within range at %f%% off****ALERT*****!!!!\n" % (var*100)
    else:
      print "\nMAD accurate and within %f%% off" % (var*100)
    
    print "==========================================================================="
  
  def testDegree(self):
    
    test = np.load(self.deg_fn)
    bench = np.load(os.path.join(self.benchdir, str(self.numNodes),"degArr.npy"))
    np.testing.assert_equal(bench, test, "Disa: Inequality testing DEGREE failure on %d test" % self.numNodes, False)
    
    print "\n**** Vertex Degrees accurate****\n"
    print "==========================================================================="
  
  def testSS1(self):
    
    test = np.load(self.ss1_fn)    
    bench = np.load(os.path.join(self.benchdir, str(self.numNodes), "scanStatArr.npy"))

    np.testing.assert_equal(bench, test, "Disa: Inequality testing SCANSTAT1 failure on %d test" % self.numNodes, False)
    
    print "\n****Scan stat 1 accurate****"
    print "==========================================================================="
  
  def testTriangles(self, tol = 0.1):
    proximityAssertion(np.load(self.tri_fn), np.load(os.path.join(self.benchdir, \
                          str(self.numNodes), "triArr.npy")), tol, "Triangle count" )
    print "==========================================================================="

  def testClustCoeff(self, tol = 0.1):
    proximityAssertion(np.load(self.ccArr_fn), np.load(os.path.join(self.benchdir,\
                          str(self.numNodes), "ccArr.npy")), tol, "Clustering coefficient")
    print "==========================================================================="
  
'''  
  def testAPL(self):
    pass

  def testSS2(self):
    pass
'''
######################### ************** #########################
#                     STAND ALONE FUNCTIONS                      #
######################### ************** #########################

def proximityAssertion(arr, benchArr, tol, testName):
  
  if len(arr) != len(benchArr):
    print testName+" Arrays unequal! Test terminated" 
    return

  diffArr = abs(np.subtract(arr, benchArr)) # difference of the two arrays
  percdiff = np.empty(len(arr))
  
  for idx in range(len(arr)):
    if benchArr[idx] != 0:
      percdiff[idx] = (diffArr[idx]/float(benchArr[idx]))
    else:
      percdiff[idx] = (diffArr[idx]/0.000001)
  
  diff = 0 if sum(percdiff) ==  0 else sum(percdiff)/float(len(percdiff))     # Average difference in bench & test
  if (abs(diff) > tol):
    print testName+" !!!!**** ALERT***** Global percent difference too high by %f%%****ALERT*****!!!!\n" % ((diff-tol)*100.0)
  else:
    print testName+" global percent difference OK! at %f%% off" % ((diff)*100.0)
