import roi
import matplotlib.pyplot

#
#  ROISlice
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
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  try:
    roix = roi.ROIXML( result.roixmlfile )
    rois = roi.ROIData ( result.roirawfile, roix.getShape() ) 
  except:
    # RBTODO give a meaningful error 
    print "Failed to parse ROI files at: ", result.roixmlfile, result.roixmlfile
    assert 0

  matplotlib.pyplot.pcolor ( rois.data[:,:,result.slice] )

  raw_input("Press Enter to continue...")

if __name__ == "__main__":
  main()
