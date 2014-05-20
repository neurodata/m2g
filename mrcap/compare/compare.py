
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


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

