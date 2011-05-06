
import sys
import os

import numpy

#
# TODO:
#  - URGENT: Fix fiber to voxel mapping
#  - Look into memory optimizatiosn
#    - Garbage collection costs?
#    - Should we use a single instance of a fiber instead of creating new ones?
#    - Is it benefical to pre-allocate for the longest fiber?
#  - Support random access
#  - Support simultaneous access
#


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

    fiberHeaderFormat = numpy.dtype([('nFiberLength','i4'),
        ('cReserved', 'i1'),
        ('rgbFiberColor','3i1'),
        ('nSelectFiberStartPoint','i4'),
        ('nSelectFiberEndPoint','i4') ])

    fiberDataFormat = numpy.dtype("3f4")

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

    def _rewind(self):
        """Skip (or rewind to) the first fiber."""
        # The first fiber is always at byte 128
        self._fileobj.seek(128, os.SEEK_SET)
        self.currentFiber = 0

    def nextFiber(self):
        """Read and return the next fiber (or None at EOF)"""
        if self.currentFiber == self.fiberCount:
            return None
        fiberHeader = numpy.fromfile(self._fileobj, dtype=self.fiberHeaderFormat, count=1)
        fiberLength = fiberHeader['nFiberLength']
        path = numpy.fromfile(self._fileobj, dtype=self.fiberDataFormat, count=fiberLength)
        self.currentFiber += 1
        return Fiber(fiberHeader, path)

    def __str__(self):
        return self.fileHeader.__str__()

    def __iter__(self):
        return FiberIterator(self)

    def __del__(self):
        self._fileobj.close()
        return;


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

class Fiber:
    def __init__(self, header, path):
        self.header = header
        self.path = path
        self.length = int(self.header['nFiberLength'])
        return

    def __str__(self):
        return self.header.__str__() + "\n" + self.path.__str__()

    def getVoxels(self):
        """Return an array with the integral voxel coordintes."""
        voxels = numpy.zeros(self.path.shape, dtype=numpy.int16)

        # Quick hack to get integer version
        # URGENT: Properly handle edge crossing
        voxels += self.path
        return voxels

