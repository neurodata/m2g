import argparse

import matplotlib.pyplot
import mask
import sys

#
#  maskslice
#
#  Draw a brain mask slice using matplotlib.pyplot as a pcolor graph
#

#
# main
#
def main ():

  parser = argparse.ArgumentParser(description='Draw the mask map of a brain.')
  parser.add_argument('maskxmlfile', action="store")
  parser.add_argument('maskrawfile', action="store")
  # RBTODO how to make 0,1,2 the legal values
  parser.add_argument('--dimensions', action="store", default="xy")
  parser.add_argument('slice', action="store")

  result = parser.parse_args()

  try:
    maskx = mask.MaskXML( result.maskxmlfile )
    masks = mask.MaskData ( result.maskrawfile, maskx.getShape() ) 
  except:
    # RBTODO give a meaningful error 
    print "Failed to parse brain mask files at: ", result.maskxmlfile, result.maskxmlfile
    sys.exit ( -1 ) 

  if result.dimensions == "xy":
    matplotlib.pyplot.pcolor ( masks.data[:,:,result.slice] )
  elif result.dimensions == "yz":
    matplotlib.pyplot.pcolor ( masks.data[result.slice,:,:] )
  elif result.dimensions == "xz":
    matplotlib.pyplot.pcolor ( masks.data[:,result.slice,:] )
  else:
    print "Choose xy, xz, or yz as dimensino or leave blank for xy default"


  raw_input("Press Enter to continue...")

if __name__ == "__main__":
  main()
