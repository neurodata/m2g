
import argparse
import matplotlib.pyplot
import numpy as np
from scipy.io import loadmat
from scipy.sparse import csc_matrix


parser = argparse.ArgumentParser(description='False color graph from a mat file')
parser.add_argument('matfile', action="store")

result = parser.parse_args()

matcontents = loadmat ( result.matfile )

graphcsc = matcontents["fibergraph"] 
graphdata = np.array (graphcsc.todense())

print graphdata [ 0:4, 0:4 ]

matplotlib.pyplot.pcolor ( graphdata[:,:] )
matplotlib.pyplot.show ()

