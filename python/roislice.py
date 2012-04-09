import argparse

#import matplotlib.pyplot
import roi
import sys

#
#  roislice
#
#  Draw an ROI XY slice using matplotlib.pyplot as a pcolor graph
#

def main ():

  parser = argparse.ArgumentParser(description='Draw the ROI map of a brain.')
  parser.add_argument('roixmlfile', action="store")
  parser.add_argument('roirawfile', action="store")
  parser.add_argument('--dimensions', action="store", default="xy", help="xy, xz, or yz")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  # Read the XML file and then the data
  try:
    roix = roi.ROIXML( result.roixmlfile )
    rois = roi.ROIData ( result.roirawfile, roix.getShape() ) 
  except:
    print "Failed to parse ROI files at: ", result.roixmlfile, result.roixmlfile
    assert 0

      
  # Counting the non-zero elements
  count = 0
  for z in range(rois.data.shape[2]):
    for y in range(rois.data.shape[1]):
      for x in range(rois.data.shape[0]):
        if rois.data[x,y,z] != 0:
          count = count + 1

  print count
  sys.exit(0)

  # cut out the specified slice
  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( rois.data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( rois.data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( rois.data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimension or leave blank for xy default"


  # display until key press
  raw_input("Press Enter to continue...")

if __name__ == "__main__":
  main()
