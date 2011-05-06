
#
# Script to transform a fiber file into a sparse adjacency matrix.
#

#
# TODO:
#  - Implement a live status bar
#  - Integrate into larger workflow
#  - Make code more readable (especially w.r.t. dimensional encoding)
#  - Clean up mixed used of arrays and tuples to store voxels
#

import argparse
import sys
from array import array

import numpy
from scipy import sparse

from fiber import FiberReader

def makeKey(voxel, shape):
    return voxel[0] * shape[1] * shape[2] + voxel[1] * shape[2] + voxel[2]

def keyToVoxel(key, shape):
    # TODO: This a hack to enable binary I/O later.  We should probably be using tuple.
    return array ('i', [key / (shape[1] * shape[2]), (key / shape[2]) % shape[1], key % shape[2]] )

def main():
    parser = argparse.ArgumentParser(description='Transform the MRI Studio files into a sprase binary matrix.')
    parser.add_argument('input', action="store", help="Source MRI Studio file")
    parser.add_argument('output', action="store", help="Root name for output files")
    parser.add_argument('--count', action="store", type=int, default=0, help="Number of fibers to read")
    parser.add_argument('--status', action="store_true", default=False, help="Show status bar")

    result = parser.parse_args()
    reader = FiberReader(result.input)

    # output file names
    spatialFileName = result.output + ".spatial"
    spatialBinaryFileName = result.output + ".spatialbinary"

    xdim = reader.shape[0] 
    ydim = reader.shape[1]
    zdim = reader.shape[2]

    maxVoxels = xdim*ydim*zdim
    seenVoxels = numpy.zeros(maxVoxels, dtype='b')

    A = sparse.dok_matrix((maxVoxels,maxVoxels), dtype='i4')
    A.setdefault(0)
    #A = sparse.lil_matrix((maxVoxels,maxVoxels), dtype='i4')

    count = 0

    if result.status:
        print "Reading fibers..."

    for fiber in reader:
        count += 1
        if result.count > 0 and count > result.count:
            break

        if result.status:
            if count % 500 == 0:
                print count

        voxels = fiber.getVoxels()
        #print fiber.length

        # Mark voxels as seen

        for source in xrange(fiber.length):
            sourceKey = makeKey(voxels[source], reader.shape)
            seenVoxels[sourceKey] = True

            for dest in xrange(source, fiber.length):
                destKey = makeKey(voxels[dest], reader.shape)

                A[sourceKey,destKey] = A[sourceKey,destKey] + 1
                A[destKey,sourceKey] = A[destKey,sourceKey] + 1

        #for i in voxels:
        #    print i
        #print voxels[0]
        #print voxels[1]


    if result.status:
        print "Finding spatial map..."

    # Loop over the list of seen voxels and...
    #  - Count the number of distinct voxels
    #  - Assign a sequential ubique ID to each voxel
    #  - Write values to a ".spatial" and ".spatialbinary" files
    spatialFile = open(spatialFileName, mode='w')
    spatialFile.write("n\tx\ty\tz\n")
    spatialBinaryFile = open(spatialBinaryFileName, mode='wb')

    voxelIdMap = numpy.zeros(maxVoxels, dtype='i4')
    voxelCount = 0
    for key in xrange(maxVoxels):
        if seenVoxels[key]: 
            voxelIdMap[key] = voxelCount
            voxel = keyToVoxel(key, reader.shape)
            spatialFile.write("{0}\t{1}\t{2}\t{3}\n".format(voxelCount, voxel[0], voxel[1], voxel[2]))
            # TODO: clean this up
            voxel.tofile(spatialBinaryFile)
            #spatialBinaryFile.write(voxel[0
            voxelCount += 1
    spatialFile.close()
    spatialBinaryFile.close()

    # No longer need fiber reader
    del reader


    if result.status:
        print "Writing sparse binary matrix..."


    return

if __name__ == "__main__":
      main()
