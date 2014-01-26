# Read a fiber file and generate the corresponding sparse graph
# @author Randal Burns, Disa Mhembere

import argparse
import sys
import os
import mrcap.roi as roi
from mrcap.fiber import FiberReader
from time import time

def genGraph(infname, outfname, roixmlname=None, roirawname=None, bigGraph=False, outformat="graphml", numfibers=0): # Edit
  """
  Generate a sparse igraph from an MRI file based on input and output names.
  Outputs a graphml formatted graph by default

  positional args:
  ================
  infname - file name of _fiber.dat file
  outfname - Dir+fileName of output .mat file
  roixmlname - file name of _roi.xml file
  roirawname - file name of _roi.raw file
  bigGraph - boolean True or False on whether to process a bigraph=True or smallgraph=False
  numfibers - the number of fibers
  """

  start = time()
  # Determine size of graph to be processed i.e pick a fibergraph module to import
  if bigGraph:
    from fibergraph_bg import FiberGraph
  else:
    from fibergraph_sm import FiberGraph

  # If these filenames are undefined then,
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
    if count == 20000:
      break

  del reader
  # Done adding edges
  fbrgraph.complete()

  fbrgraph.saveToIgraph(outfname, gformat=outformat)

  del fbrgraph
  print "\nGraph building complete in %.3f secs" % (time() - start)
  return

def main ():

  parser = argparse.ArgumentParser( description="Read the contents of MRI Studio file and generate a sparse connectivity graph in SciDB." )
  parser.add_argument( "fbrfile", action="store" )
  parser.add_argument( "output", action="store", help="resulting name of graph")

  parser.add_argument( "--outformat", "-f", action="store", default="graphml", help="The output graph format i.e. graphml, gml, dot, pajek etc..")
  parser.add_argument( "--isbig", "-b", action="store_true", default=False, help="Is the graph big? If so use this flag" )
  parser.add_argument( "--roixml", "-x", action="store", default=None, help="The full file name of roi xml file" )
  parser.add_argument( "--roiraw", "-w", action="store", default=None, help="The full file name of roi raw file" )
  parser.add_argument( "--numfib", "-n", action="store", type=int, default=-1, help="The number of fibers ..." )

  result = parser.parse_args()

  genGraph ( result.fbrfile, result.output, result.roixml, result.roiraw, result.isbig, result.outformat, result.numfib )

if __name__ == "__main__":
  main()
