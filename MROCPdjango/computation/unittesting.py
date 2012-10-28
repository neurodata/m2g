import numpy as np
import os

#Global filenames

class test():
  def __init__(self, G_fn, dataDir, numNodes, ss1_fn = None, deg_fn = None, tri_fn = None, ccArr_fn = None):
    self.G_fn = G_fn
    self.numNodes = numNodes
    self.ss1_fn = ss1_fn 
    self.deg_fn = deg_fn
    self.tri_fn = tri_fn
    self.ccArr_fn = ccArr_fn
    self.dataDir = dataDir
    self.benchdir = 'bench'
    
    if not os.path.exists(dataDir):
      os.makedirs(dataDir)
  
  def testDegree(self):
    #for num in [10,50,100]:
    #deg_fn = os.path.join(benchdir,str(self.numNodes),self.degArr)
    
    test = np.load(self.deg_fn)
    bench = np.load(os.path.join(self.benchdir, str(self.numNodes),"degArr.npy"))
    np.testing.assert_equal(bench, test, "Disa: Inequality testing DEGREE failure on %d test" % self.numNodes, False)
    
    print "\n****Successful degree test****"
  
  def testSS1(self):
    #for num in [10,50,100]:
    #scanStatArr_fn = os.path.join(self.benchdir,str(self.numNodes),self.scanStatArr)

    test = np.load(self.ss1_fn)    
    bench = np.load(os.path.join(self.benchdir, str(self.numNodes), "scanStatArr.npy"))

    np.testing.assert_equal(bench, test, "Disa: Inequality testing SCANSTAT1 failure on %d test" % self.numNodes, False)
    
    print "\n****Successful test scan stat test****"
  
  def testTriangles(self):
    #for num in [10,50,100]:      
    #triArr_fn = os.path.join(self.benchdir,str(self.numNodes),self.triArr)
      
    test = np.load(self.tri_fn)
    bench = np.load(os.path.join(self.benchdir, str(self.numNodes), "triArr.npy"))
    
    np.testing.assert_equal(bench,test,"Disa: Inequality testing TRIANGLE failure on %d test" % self.numNodes, False)
    
  '''
  def testClustCoeff():
    #for num in [10,50,100]:      
    ccArr_fn = os.path.join(self.benchdir,str(self.numNodes),self.ccArr)
    testcArr_fn = os.path.join(self.benchdir,str(self.numNodes),"test_clustcoeff.npy")
      
    np.load(ccArr)
    np.load(testcArr_fn)
    
    np.testing.assert_equal(bench,test,"Disa: Inequality testing TRIANGLE failure on %d test" % self.numNodes, False)
  
  # print "\n\n****REMEMBER TO CHECK MAX AVERAGE DEGREE*****"
  
  def testAPL():
    pass

  def testSS2():
    pass
'''