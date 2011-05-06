/* 
 * Small program to copy Sparse Binary to Sparse Text file format
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
  const char * ifname; 

  if (argc == 2) {
    ifname = argv[1];
  } else {
    printf("%s <input>\n", argv[0]);
    return 1;
  }
  int ifd;
  if ( (ifd = open(ifname, O_RDONLY | O_LARGEFILE)) == -1) {
    perror(ifname);
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
  printf("%d %d %d\n", header.numRows, header.numCols, header.totalNonZeroValues);
  for (int col = 0; col < header.numCols; col++) {
    read(ifd, &numNonZeroValues, sizeof(int)); 
    printf("%d\n", numNonZeroValues);
    for(int row = 0; row < numNonZeroValues; row++) {
      read(ifd, &rowContent, sizeof(rowEntry)); 
      printf("%d %.1f\n", rowContent.rowIndex, rowContent.value);
    }
  }

  return 0;
}
