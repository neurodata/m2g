
import sys
import os
import zindex

import numpy


class FiberReader:
    """Class to read data file stored in MRI Studio format.
       The file format is documented at https://www.mristudio.org/wiki/faq
    """

    headerFormat = numpy.dtype([('sFiberFileTag','a8'),
        ('nFiberNr','i4'), ('nFiberLenMax','i4'), ('fFiberLenMean','f4'),
        ('nImgWidth','i4'), ('nImgHeight','i4'), ('nImgSlices', 'i4'),
        ('fPixelSizeWidth','f4'), ('fPixelSizeHeight','f4'), ('fSliceThickness','f4'),
        ('enumSliceOrientation','i1'), ('enumSliceSequencing','i1'),
        ('sVersion','a8') ])


    # StartPoint is the fiber offset, typically 0, i.e. the 0th fiber in the list
    # EndPoint is the end fiber offset, typically k in a list of k files
    fiberHeaderFormat = numpy.dtype([('nFiberLength','i4'),
        ('cReserved', 'i1'),
        ('rgbFiberColor','3i1'),
        ('nSelectFiberStartPoint','i4'),
        ('nSelectFiberEndPoint','i4') ])

    fiberDataFormat = numpy.dtype("3f4")

    #
    #  Constructor -- reads metadata in header
    #    and gets shape information
    #
    def __init__(self, filename):
        self._filename = filename
        self._fileobj = open(self._filename, mode='rb')

        # Read the header
        #headerfmt = np.dtype("a8, i4, i4, f4, i4, i4, i4, f4, f4,f4, a1, a1, a8")

        self.fileHeader = numpy.fromfile(self._fileobj, dtype=self.headerFormat, count=1)

        # Should we keep the long names?
        self.nImgWidth = int(self.fileHeader['nImgWidth'])
        self.nImgHeight = int(self.fileHeader['nImgHeight'])
        self.nImgSlices = int(self.fileHeader['nImgSlices'])

        self.shape = ( int(self.fileHeader['nImgWidth']),
            int(self.fileHeader['nImgHeight']),
            int(self.fileHeader['nImgSlices']) )

        # Verify file tag
        if self.fileHeader['sFiberFileTag'] != 'FiberDat':
            raise Exception("Invalid file tag found.")

        self.fiberCount = self.fileHeader["nFiberNr"]
        self.fiberLengthMax = self.fileHeader["nFiberLenMax"]
        self.currentFiber = 0

        # Position at first fiber
        self._rewind()

        self.nextFiber()

    #
    #  Go the first fiber location.  Not part of the iterator abstraction
    #
    def _rewind(self):
        """Skip (or rewind to) the first fiber."""
        # The first fiber is always at byte 128
        self._fileobj.seek(128, os.SEEK_SET)
        self.currentFiber = 0

    #
    #  Get the next fiber in the file
    #
    def nextFiber(self):
        """Read and return the next fiber (or None at EOF)"""
        if self.currentFiber == self.fiberCount:
            return None
        fiberHeader = numpy.fromfile(self._fileobj, dtype=self.fiberHeaderFormat, count=1)
        fiberLength = fiberHeader['nFiberLength']
        path = numpy.fromfile(self._fileobj, dtype=self.fiberDataFormat, count=fiberLength)
        self.currentFiber += 1
        return Fiber(fiberHeader, path)

    #
    #  Support the str() function on this object
    #
    def __str__(self):
        return self.fileHeader.__str__()

    #
    #  Make object iterable
    #
    def __iter__(self):
        return FiberIterator(self)

    #
    #  Close the file on destruction
    #
    def __del__(self):
        self._fileobj.close()
        return;


#
#  Iterator class to support FiberReader
#
class FiberIterator:
    def __init__(self, reader):
      self.reader = reader
      self.reader._rewind()

    def __iter__(self):
      return self

    def next(self):
        fiber = self.reader.nextFiber()
        if fiber:
            return fiber
        else:
            raise StopIteration



#
#  Fiber abstraction
#
class Fiber:

    # just a small value to pull points on faces into next lower cubes
    _epsilon = 0.001

    def __init__(self, header, path):
        self.header = header
        self.path = path
        self.length = int(self.header['nFiberLength'])
        return

    def __str__(self):
        return self.header.__str__() + "\n" + self.path.__str__()
    
    #
    #  Return a list of voxels in this Fiber.  As tuples by zindex
    #
    def getVoxels (self):
      """Return the list of edges in this fiber. As tuples"""

      voxels = []

      # extract a path of vertices
      for fbrpt in self.path: 

        # on an X face
        if ( fbrpt[0] % 1.0 == 0.0 ):
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]-self._epsilon), int(fbrpt[1]), int(fbrpt[2]) ] ))
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]), int(fbrpt[2]) ] ))

        # on a Y face
        elif ( fbrpt[1] % 1.0 == 0.0 ):
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]-self._epsilon), int(fbrpt[2]) ] ))
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]), int(fbrpt[2]) ] ))

        # on a Z face
        elif ( fbrpt[2] % 1.0 == 0.0 ):
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]), int(fbrpt[2]-self._epsilon) ] ))
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]), int(fbrpt[2]) ] ))

        # if in the middle of a voxel no edge
        elif (( fbrpt[0] % 1.0 != 0.0 ) and ( fbrpt[1] % 1.0 != 0.0 ) and ( fbrpt[2] % 1.0 != 0.0 )):
           pass

        # Data shouldn't be on corners or edges
        else:
          print "Data shouldn't be on corners or edges"
          assert 0

      # eliminate duplicates
      return set ( voxels )

