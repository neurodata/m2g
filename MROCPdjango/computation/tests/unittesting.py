import numpy as np
import os

#Global filenames

class test():
  def __init__(self, G_fn, dataDir, numNodes, ss1_fn = None, deg_fn = None, tri_fn = None, ccArr_fn = None, mad = None, benchdir=None):
    self.G_fn = G_fn
    self.numNodes = numNodes
    self.ss1_fn = ss1_fn 
    self.deg_fn = deg_fn
    self.tri_fn = tri_fn
    self.ccArr_fn = ccArr_fn
    self.dataDir = dataDir
    self.mad = mad
    self.benchdir = benchdir
    
    if not os.path.exists(dataDir):
      os.makedirs(dataDir)
  
  def testMAD(self, tol = 0.1):
    
    benchMAD = float(np.load(os.path.join(self.benchdir, str(self.numNodes),'MAD.npy')))
    var = abs(benchMAD - np.load(self.mad).item())/benchMAD 
    if (var  > tol):
      print "\n!!!!**** ALERT***** MAD is not within tolerance at %f%% off****ALERT*****!!!!\n" % (var*100)
    else:
      print "\nMAD accurate and within %f%% of actual .." % (var*100)
    
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
    print "==========================================================================="
    proximityAssertion(np.load(self.ccArr_fn), np.load(os.path.join(self.benchdir,\
                          str(self.numNodes), "ccArr.npy")), tol, "Clustering coefficient")
    print "==========================================================================="
######################### ************** #########################
#                     STAND ALONE FUNCTIONS                      #
######################### ************** #########################

def proximityAssertion(arr, benchArr, tol, testName):
  
  if len(arr) != len(benchArr):
    print testName+" Arrays unequal! Test terminated" 
    return

  diffArr = abs(arr - benchArr) # difference of the two arrays
  meanArr = map(ave, zip(arr, benchArr))
  percdiff = map(div, zip(diffArr, meanArr))
  globalPercDiff =  (sum(percdiff)/len(arr))*100.0
  
  if (abs(globalPercDiff) > tol*100.0):
    print testName+" !!!!**** ALERT***** Global percent difference too high by %f%%****ALERT*****!!!!\n" % ((globalPercDiff-tol*100.0))
  else:
    print testName+" global percent difference OK! at %f%% off" % (globalPercDiff)
    
  return globalPercDiff

def ave(args):
  return (args[0]+args[1])/2.0

def div(args):
  num = args[0]
  den = args[1]
  if num == 0 and den == 0:
    return 0
  else:
    return num/float(den)
