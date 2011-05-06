
#
# Verify that the seed locations of fibers map to labeled
# regions of the brain.
#
# This is a sanity check to see if data files are being read correctly.
#


import argparse
import sys

import numpy

from fiber import FiberReader

def main():
    parser = argparse.ArgumentParser(description="Verify fibers seeds are labeled")
    parser.add_argument('fiberfile', action="store")
    parser.add_argument('labelfile', action="store") 
    parser.add_argument('--count', action="store", type=int, default=-1)
    #parser.add_argument('outfile', action="store", nargs="?") 

    result = parser.parse_args()

    reader = FiberReader(result.fiberfile)
    count = result.count

    # open the matlab file
    labelfile = open(result.labelfile, 'rb')
    labels = numpy.fromfile(labelfile, dtype='(256,256)>i4', count=199)
    #labels = numpy.fromfile(labelfile, dtype='(199,256)>i4', count=256)

    seen = numpy.zeros(71, dtype='i4')

    for fiber in reader:
        if count == 0:
            break
        elif count > 0:
            count -= 1

        for row in fiber.path:
            if row[0] % 1 == 0.5 and row[1] % 1 == 0.5 and row[2] % 1 == 0.5:
                x = int(row[0]) - 1 
                y = int(row[1]) - 1
                z = int(row[2]) - 1
                label = labels[z,y,x]
                #label = labels[x,y,z]
                if (label > 100):
                    label -= 65

                seen[label] += 1
                #print label
                #print row

    for x in xrange(71):
        print "{0}: {1}".format(x, seen[x])

if __name__ == "__main__":
      main()
