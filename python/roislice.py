import argparse

import matplotlib.pyplot
import roi

#
#  roislice
#
#  Draw an ROI XY slice using matplotlib.pyplot as a pcolor graph
#

#
# main
#
def main ():

  parser = argparse.ArgumentParser(description='Draw the ROI map of a brain.')
  parser.add_argument('roixmlfile', action="store")
  parser.add_argument('roirawfile', action="store")
  # RBTODO how to make 0,1,2 the legal values
  parser.add_argument('--dimensions', action="store", default="xy")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  try:
    roix = roi.ROIXML( result.roixmlfile )
    rois = roi.ROIData ( result.roirawfile, roix.getShape() ) 
  except:
    # RBTODO give a meaningful error 
    print "Failed to parse ROI files at: ", result.roixmlfile, result.roixmlfile
    assert 0

  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( rois.data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( rois.data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( rois.data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimensino or leave blank for xy default"


  raw_input("Press Enter to continue...")

if __name__ == "__main__":
  main()
