
import argparse
import matplotlib.pyplot
import numpy as np
import csv

parser = argparse.ArgumentParser(description='False color graph from a csv file')
parser.add_argument('csvfile', action="store")

result = parser.parse_args()

# Read the csv file
#graphdata = np.genfromtxt(result.csvfile, dtype=None, delimiter=',', names=True)

reader = csv.reader(open(result.csvfile,"rb"))
graphdata = np.array([[float(col) for col in row] for row in reader])
#graphdata = np.array([float(col) for col in row] for row in reader])

print graphdata.shape

print graphdata[1:5,1:5]


matplotlib.pyplot.pcolor ( graphdata[:,:] )


raw_input("Press Enter to continue...")
