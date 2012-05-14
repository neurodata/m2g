
import sys
import os
import zindex

import numpy

import nibabel.trackvis as niv


class FiberReader:
    """Class to read data file stored in TrackVis .trk format.
       The file format is documented at NiPype and NiBabel
    """

    #
    #  Constructor -- reads metadata in header
    #    and gets shape information
    #
    def __init__(self, filename):
        """Load the TrackVis file """
        self._filename = filename

        self.tracks, self.fiberHeader = niv.read(filename)
        self.fiberCount = self.fiberHeader['n_count'].ravel()[0]
        
        print "number of fibers ->", self.fiberCount
        self.currentFiber = 0
        self.shape = tuple(self.fiberHeader['dim'])

        # Position at first fiber
        self._rewind()

    #
    #  Go the first fiber location.  Not part of the iterator abstraction
    #
    def _rewind(self):
        """Skip (or rewind to) the first fiber."""
        # The first fiber is always at byte 128
        self.currentFiber = 0

    #
    #  Get the next fiber in the file
    #
    def nextFiber(self):
        """Read and return the next fiber (or None at EOF)"""

        if self.currentFiber == self.fiberCount:
            return None

        fiberLength = len(self.tracks[self.currentFiber][0])
        track = self.tracks[self.currentFiber][0]
        self.currentFiber += 1
        return Fiber(self.fiberHeader, track, fiberLength)

    #
    #  Support the str() function on this object
    #
    def __str__(self):
        return self.fiberHeader.__str__()


    #
    #  Make object iterable
    #
    def __iter__(self):
        return FiberIterator(self)


#
#  Iterator class to support FiberReader
#
class FiberIterator:
    """Iterator for TrackVis tracks"""
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


# RBTODO the header doesn't format well.

#
#  Fiber abstraction
#
class Fiber:
    """A TrackVis track"""

    def __init__(self, header, track, length):
        self.header = header
        self.track = track
        self.length = int(length)
        return

    def __str__(self):
        return self.header.__str__() + "\n" + self.track.__str__()
    
    #
    #  Return a list of voxels in this Fiber.  As tuples by zindex
    #
    def getVoxels (self):
      """Return the list of edges in this fiber. As tuples."""

      voxels = []

      #  This is corrected to match the logic of MRCAP
      # extract a track of vertices
      for fbrpt in self.track: 
        
          voxels.append ( zindex.XYZMorton ( [ int(fbrpt[0]), int(fbrpt[1]), int(fbrpt[2]) ] ))

      # eliminate duplicates
      return set ( voxels )

