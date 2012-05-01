
import argparse
import matplotlib.pyplot
import numpy as np
from scipy.io import loadmat
from scipy.sparse import csc_matrix
import csv


parser = argparse.ArgumentParser(description='False color graph from a mat file')
parser.add_argument('matfile', action="store")
parser.add_argument('csvfile', action="store")

result = parser.parse_args()

matcontents = loadmat ( result.matfile )

matcsc = matcontents["fibergraph"] 
matdata = np.array (matcsc.todense())

reader = csv.reader(open(result.csvfile,"rb"))
csvdata = np.array([[float(col) for col in row] for row in reader])

for j in range (matdata.shape[1]):
  for i in range (matdata.shape[0]):
    if matdata [ i,j ] == 0 and csvdata [i,j] != 0:
      print "Nonzero csv data at ", i,j
    if csvdata [ i,j ] == 0 and matdata [i,j] != 0:
      print "Nonzero mat data at ", i,j


