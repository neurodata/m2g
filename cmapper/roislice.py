import argparse
import numpy as np

import matplotlib.pyplot
import sys

#
#  roislice
#
#  Draw an ROI XY slice using matplotlib.pyplot as a pcolor graph
#

def main ():

  parser = argparse.ArgumentParser(description='Draw the ROI map of a brain.')
  parser.add_argument('npfile', action="store")
  parser.add_argument('--dimensions', action="store", default="xy", help="xy, xz, or yz")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  # Read the XML file and then the data
  try:
    data = np.load ( result.npfile )
  except:
    print "Failed to parse file: ", result.npfile
    sys.exit(-1)


  # cut out the specified slice
  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimension or leave blank for xy default"

  matplotlib.pyplot.show()


if __name__ == "__main__":
  main()
