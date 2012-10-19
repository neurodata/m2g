import numpy as np
import os

#Global filenames

class test():
  benchdirNm = "bench"
  aplArr = "aplArr"
  ccArr = "ccArr"
  degArr = "degArr"
  scanStatArr = "scanStatArr"
  triArr = "triArr"   
  
  def __init__(self,num):
    self.num = num

  def testDegree():
    #for num in [10,50,100]:
    deg_fn = os.path.join(benchdirNm,str(self.num),self.degArr)
    
    bench = np.load(deg_fn)
    test = np.load("test_degree.npy")
  
    np.testing.assert_equal(bench,test,"Disa: Inequality testing DEGREE failure on %d test" % self.num, False)
  
  def testSS1():
    #for num in [10,50,100]:
    scanStatArr_fn = os.path.join(benchdirNm,str(self.num),self.scanStatArr)
    
    np.load(scanStatArr)
    np.load("test_scanstat1.npy")
    
    np.testing.assert_equal(bench,test,"Disa: Inequality testing SCANSTAT1 failure on %d test" % self.num, False)
  
  
  def testTriangles():
    #for num in [10,50,100]:      
    triArr_fn = os.path.join(benchdirNm,str(self.num),self.triArr)
      
    np.load(triArr)
    np.load("test_triangles.npy")
    
    np.testing.assert_equal(bench,test,"Disa: Inequality testing TRIANGLE failure on %d test" % self.num, False)
    
  
  def testClustCoeff():
    #for num in [10,50,100]:      
    ccArr_fn = os.path.join(benchdirNm,str(self.num),self.ccArr)
    testcArr_fn = os.path.join(benchdirNm,str(self.num),"test_clustcoeff.npy")
      
    np.load(ccArr)
    np.load(testcArr_fn)
    
    np.testing.assert_equal(bench,test,"Disa: Inequality testing TRIANGLE failure on %d test" % self.num, False)
  
  # REMEMBER TO CHECK MAX AVERAGE DEGREE
  
  def testAPL():
    pass

  def testSS2():
    pass