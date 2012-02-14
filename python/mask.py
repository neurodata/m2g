import sys
import os
import xml.dom.minidom

import numpy as np

#
#  Makes a ton of assumptions about the XML data.  
#  Totally customize for MRCAP data.  Needs to be checked with 
#  anything that's not the original 109 data files on braingraph1
#
class MaskXML:
  """"Class to read the *.xml file and pull out important parameters"""

  def __init__(self,filename):

    # Parse the XML document
    self._xmldoc = xml.dom.minidom.parse(filename)

  # There are three extents.  These are the dimensions.
  def getShape ( self ):

# RBTODO should probably assert on the assumptions.  Endianess what else?
     dims = self._xmldoc.getElementsByTagName ( 'Extents' )
     return [ int(dims[0].firstChild.nodeValue), int(dims[1].firstChild.nodeValue), int(dims[2].firstChild.nodeValue) ]



class MaskData:
  """Class to read mask data derived from MRCAP.""" 

  # Get the dimension
  def __init__(self, filename, dim):

    self._filename = filename
    self._fileobj = open(self._filename, mode='rb')

    # file is a list of bytes
    self.data = np.fromfile(self._fileobj, dtype='b', count=dim[0]*dim[1]*dim[2])

    self.data = np.reshape ( self.data, dim, order='F' )



  # Is the location in the brain or not?
  def get ( self, index ):
    """Is the location in the brain or not?"""

    if index[0] >= self.data.shape[0] or index[1] >= self.data.shape[1] or index[2] >= self.data.shape[2]: 
      return 0
    return self.data [ index[0], index[1], index[2] ]

