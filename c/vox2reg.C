/* 
 * Map the voxels to regions of the brain, and recompute
 * the adjacency matrix.
 *
 * Uses the sparse binary and "spatial" output from freader,
 * as well as the voxel to region info.
 */


#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#define _FILE_OFFSET_BITS 64
#define _LARGEFILE64_SOURCE
#define _LARGEFILE_SOURCE

#ifndef O_LARGEFILE
#define O_LARGEFILE 0
#endif

int main (int argc, char **argv) {
  const char * sbname; 
  const char * spatialname;
  const char * regionfile;

  int weights = 0;

  if (argc == 4 || argc == 5) {
    sbname = argv[1];
    spatialname = argv[2];
    regionfile = argv[3];
    if (argc == 5) {
      weights = atoi(argv[4]);
    }
  } else {
    printf("%s <sparse binary file> <voxel-spatial file> <voxel region file> [weights (0|1)]\n", argv[0]);
    return 1;
  }
  int ifd;
  if ( (ifd = open(sbname, O_RDONLY | O_LARGEFILE)) == -1) {
    perror(sbname);
    return 1;
  }

  int vrfd;
  if ( (vrfd = open(regionfile, O_RDONLY | O_LARGEFILE)) == -1) {
    perror(regionfile);
    return 1;
  }



  struct sparseBinaryHeader {
      int numRows;
      int numCols;
      int totalNonZeroValues;
  } header;
  int numNonZeroValues;
  struct rowEntry {
    int rowIndex;
    float value;
  } rowContent;

  read(ifd, &header, sizeof(struct sparseBinaryHeader)); 
  //printf("%d %d %d\n", header.numRows, header.numCols, header.totalNonZeroValues);

  //printf("Opening spatial file...\n");
  FILE * spfd = fopen(spatialname, "r");
  if (spfd == NULL) {
    perror(spatialname);
    return 1;
  }
  char tempChar[255];
  // read header line to dev null
  fgets(tempChar, sizeof(tempChar), spfd);
  
  typedef struct voxelInfo {
    int voxel;
    int x;
    int y;
    int z;
  } voxelInfo;

  voxelInfo *voxels = new voxelInfo[header.numRows];

  for (int i = 0; i < header.numRows; i++) {
    fscanf(spfd, "%d %d %d %d", &voxels[i].voxel,
    &voxels[i].x,
    &voxels[i].y,
    &voxels[i].z);
    //printf("%d %d %d %d\n", voxels[i].voxel, voxels[i].x, voxels[i].y, voxels[i].z);
  }
  fclose(spfd);

  //printf("Reading region file...\n");
  /* Todo: Read all of these from the .XML file */
  int xdim = 256;
  int ydim = 256;
  int zdim = 199;
  
  int filesize = xdim*ydim*zdim*sizeof(int);

  // todo: replace with mmap
  int *regionmap = new int[filesize];
  bzero(regionmap, filesize);

  int totalBytesRead = 0;
  while (totalBytesRead < filesize) {
    int bytesRead = read(vrfd, (char *)regionmap + totalBytesRead, 16384);
    if (bytesRead < 0) {
      perror(regionfile);
      return 1;
    }

    totalBytesRead += bytesRead;
  }
  assert(totalBytesRead == filesize);

  /*for (int i = 0; i < xdim*ydim*zdim; i++) { 
    if (regionmap[i]) {
      //printf("%d - %d\n", i, ntohl(regionmap[i]));
      printf("%d %d %d\n", i % 256, (i / 256) % 256, (i / (256*256)));
      //printf("%d %d %d\n", i % 256, (i / 256) % 256, (i / (256*199)));
    }
  } */

  close(vrfd);

  int *voxelToRegion = new int[header.numRows];

  for (int i = 0; i < header.numRows; i++) {
    //for (int v = -1; v <= 1; v++) {
    voxelInfo voxel = voxels[i];
    /*voxel.x = 156;
    voxel.y = 159;
    voxel.z = 159;  */
    /*
    printf("%d %d %d %d %d %d %d %d\n",
    ntohl(regionmap[voxel.x*xdim*xdim + voxel.y*xdim + voxel.z]),
    ntohl(regionmap[voxel.x*zdim*xdim + voxel.y*zdim + voxel.z]),
    regionmap[voxel.x*xdim*ydim + voxel.y*ydim + voxel.z],
    regionmap[voxel.x*zdim*ydim + voxel.y*ydim + voxel.z],
    regionmap[voxel.z*xdim*ydim + voxel.y*ydim + voxel.x],
    regionmap[voxel.z*zdim*ydim + voxel.y*ydim + voxel.x],
    regionmap[voxel.z*xdim*xdim + voxel.y*xdim + voxel.x],
    regionmap[voxel.z*zdim*xdim + voxel.y*zdim + voxel.x]);
    //}*/

    int region = ntohl(regionmap[voxel.x*xdim*ydim + voxel.y*xdim + voxel.z]);
    //int region = ntohl(regionmap[voxel.z*xdim*ydim + voxel.y*xdim + voxel.x]);
    // regLabel(regLabel > 100) = regLabel(regLabel > 100) + 65;
    if (region > 100) { region -= 65; }
    /*if (region)  {
      printf("%d: %d %d %d -> %d\n", voxel.voxel, voxel.x, voxel.y, voxel.z, region); 
     }
      */
     voxelToRegion[i] = region;
  }

  delete [] regionmap;

  long stats[71][71];
  bzero(stats, sizeof(long) * 71 * 71);
  
  /* Now iterate through sb file */
  for (int col = 0; col < header.numCols; col++) {
    read(ifd, &numNonZeroValues, sizeof(int)); 
    int start = voxelToRegion[col];
    //printf("%d\n", numNonZeroValues);
    for(int row = 0; row < numNonZeroValues; row++) {
      read(ifd, &rowContent, sizeof(struct rowEntry)); 
      int end = voxelToRegion[rowContent.rowIndex];
      //printf("%d to %d\n", start, end);
      //printf("%d %.1f\n", rowContent.rowIndex, rowContent.value);
      if (weights) {
        stats[start][end] += (int) rowContent.value;
        if (start != end) {
          stats[end][start] += (int) rowContent.value;
        }
      }
      stats[start][end]++;
      if (start != end) {
        stats[end][start]++;
      }
    }
  }

  delete [] voxels;
  delete [] voxelToRegion;
  close(ifd);

  for (int x = 0; x <= 70; x++) {
    for (int y = 0; y <= 70; y++) {
      printf("%ld ", stats[x][y]);
    }
    printf("\n");
  }


  return 0;
}
