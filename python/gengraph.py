#
#
# Read a fiber file and generate the corresponding sparse graph
#
#

import argparse
import sys
import os
import roi
import mask
#from fibergraph import FiberGraph
from fibergraph_sm import FiberGraph
from fiber import FiberReader


#
# Generate a sparse graph of an MRI file 
#   based on input and output names.
#   Outputs a matlab file. 
#
def genGraph( infname, outfname, numfibers ):
  """Generate a sparse graph from an MRI studio file and write it as a Matlab file"""

  # Assume that there are ROI files in ../roi
  [ inpathname, inbasename ] = os.path.split ( infname )
  inbasename = str(inbasename).rpartition ( "_" )[0]
  roifp = os.path.normpath ( inpathname + '/../roi/' + inbasename )
  roixmlname = roifp + '_roi.xml'
  roirawname = roifp + '_roi.raw'

  # Assume that there are mask files in ../mask
  maskfp = os.path.normpath ( inpathname + '/../mask/' + inbasename )
  maskxmlname = maskfp + '_binmask.xml'
  maskrawname = maskfp + '_binmask.raw'


  # Get the ROIs
  try:
    roix = roi.ROIXML( roixmlname )
    rois = roi.ROIData ( roirawname, roix.getShape() )
  except:
    print "ROI files not found at: ", roixmlname, roirawname
    sys.exit (-1)

  # Get the mask
  try:
    maskx = mask.MaskXML( maskxmlname )
    masks = mask.MaskData ( maskrawname, maskx.getShape() )
  except:
    print "Mask files not found at: ", maskxmlname, maskrawname
    sys.exit (-1)

  # Create fiber reader
  reader = FiberReader( infname )

  # Create the graph object
  # get dims from reader
  fbrgraph = FiberGraph ( reader.shape, rois, masks )

  print "Parsing MRI studio file {0}".format ( infname )

  # Print the high-level fiber information
  print(reader)

  count = 0

  # iterate over all fibers
  for fiber in reader:
    count += 1
    # add the contribution of this fiber to the 
    fbrgraph.add(fiber)
    if numfibers > 0 and count >= numfibers:
      break
    if count % 10000 == 0:
      print ("Processed {0} fibers".format(count) )

  print "Deleting the reader"

  del reader

  print "Completing the graph"
  # Done adding edges
  fbrgraph.complete()

  print "Saving matlab file"
  # Save a version of this graph to file
  fbrgraph.saveToMatlab ( "fibergraph", outfname )

  # Load a version of this graph from  
#  fbrgraph.loadFromMatlab ( "fibergraph", outfname )

  del fbrgraph
  
  return



#
# main
#
def main ():

  parser = argparse.ArgumentParser(description='Read the contents of MRI Studio file and generate a sparse connectivity graph in SciDB.')
  parser.add_argument('--count', action="store", type=int, default=-1)
  parser.add_argument('fbrfile', action="store")
  parser.add_argument('output', action="store")

  result = parser.parse_args()
  genGraph ( result.fbrfile, result.output, result.count )

  if 1:
    from fibergraph_sm import FiberGraph
  else:     
    from fibergraph import FiberGraph
 


if __name__ == "__main__":
  main()
