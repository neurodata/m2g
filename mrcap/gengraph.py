'''
 Read a fiber file and generate the corresponding sparse graph
 @author randalburns

 - minor edits for web service by: Disa Mhembere
'''

import argparse
import sys
import os
import roi
#import mask
#from fibergraph import FiberGraph
#from fibergraph_sm import FiberGraph
from fiber import FiberReader


#
# Generate a sparse graph of an MRI file
#   based on input and output names.
#   Outputs a matlab file.
#
def genGraph(infname, outfname, roixmlname = None, roirawname = None, bigGraph = False , numfibers=0): # Edit
  """
  infname - file name of _fiber.dat file
  outfname - Dir+fileName of output .mat file
  roixmlname - file name of _roi.xml file
  roirawname - file name of _roi.raw file
  bigGraph - boolean True or False on whether to process a bigraph=True or smallgraph=False
  numfibers - the number of fibers
  """

  """Generate a sparse graph from an MRI studio file and write it as a Matlab file"""

  # Disa Edit - Determine size of graph to be processed i.e pick a fibergraph module to import
  if bigGraph:
    from fibergraph import FiberGraph
  else:
    from fibergraph_sm import FiberGraph

  # Disa Edit - if these filenames are undefined then,
  # assume that there are ROI files in ../roi

  if not(roixmlname and roirawname):
    [ inpathname, inbasename ] = os.path.split ( infname )
    inbasename = str(inbasename).rpartition ( "_" )[0]
    roifp = os.path.normpath ( inpathname + '/../roi/' + inbasename )
    roixmlname = roifp + '_roi.xml'
    roirawname = roifp + '_roi.raw'

#  # Assume that there are mask files in ../mask
#  maskfp = os.path.normpath ( inpathname + '/../mask/' + inbasename )
#  maskxmlname = maskfp + '_mask.xml'
#  maskrawname = maskfp + '_mask.raw'

  # Get the ROIs

  try:
    roix = roi.ROIXML( roixmlname ) # Create object of type ROIXML
    rois = roi.ROIData ( roirawname, roix.getShape() )
  except:
    raise Exception("ROI files not found at: %s, %s" % (roixmlname, roirawname))

  # Get the mask
#  try:
#    maskx = mask.MaskXML( maskxmlname )
#    masks = mask.MaskData ( maskrawname, maskx.getShape() )
#  except:
#    print "Mask files not found at: ", maskxmlname, maskrawname
#    sys.exit (-1)

  # Create fiber reader
  reader = FiberReader( infname )

  # Create the graph object
  # get dims from reader
# fbrgraph = FiberGraph ( reader.shape, rois, masks )
  fbrgraph = FiberGraph ( reader.shape, rois, None )

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

def main ():

  parser = argparse.ArgumentParser(description='Read the contents of MRI Studio file and generate a sparse connectivity graph in SciDB.')
  parser.add_argument( '--count', action="store", type=int, default=-1 )
  parser.add_argument( 'fbrfile', action="store" )
  parser.add_argument( 'output', action="store" )

  result = parser.parse_args()

  genGraph ( result.fbrfile, result.output, result.count )

if __name__ == "__main__":
  main()
