/* Fiber Data Reader
 * [code borrowed from https://www.mristudio.org/wiki/faq]
 */

using namespace std;

#include <vector>
#include <set>
#include <bitset>
#include <map>

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

#ifdef __APPLE__
#  define off64_t off_t
#  define fopen64 fopen
#endif

#define _FILE_OFFSET_BITS 64
#define _LARGEFILE64_SOURCE
#define _LARGEFILE_SOURCE

#ifndef O_LARGEFILE
#define O_LARGEFILE 0
#endif

struct stFiberFileHeader {
  char sFiberFileTag[8]; // file tag = FiberDat
  int nFiberNr; // total number of fibers
  int nFiberLenMax; // max-length of fibers
  float fFiberLenMean; // mean-length of fibers
  int nImgWidth; // image dimension
  int nImgHeight;
  int nImgSlices;
  float fPixelSizeWidth; // voxel size
  float fPixelSizeHeight;
  float fSliceThickness;
  unsigned char enumSliceOrientation; // slice orientation
  unsigned char enumSliceSequencing; // slice sequencing
  char sVersion[8]; // version number
}; // Get file name using File-Open diaglog

typedef struct RGB_TRIPLE {
  unsigned char r;
  unsigned char g;
  unsigned char b;
} RGB_TRIPLE;

typedef struct XYZ_TRIPLE {
  float x;
  float y;
  float z;
} XYZ_TRIPLE;

typedef struct Voxel {
  unsigned int x;
  unsigned int y;
  unsigned int z;

  Voxel (int x1, int y1, int z1) : x(x1), y(y1), z(z1) { }
  Voxel () : x(0), y(0), z(0) { }
} Voxel;



struct Fiber {
  struct {
    int nFiberLength; // fiber length
    unsigned char cReserved;
    RGB_TRIPLE rgbFiberColor; // R-G-B, 3 bytes totally
    int nSelectFiberStartPoint;
    int nSelectFiberEndPoint;
  } header;
  XYZ_TRIPLE *xyzFiberCoordinate;
};

unsigned int makeKey(XYZ_TRIPLE xyz, unsigned int xdim, unsigned int ydim, unsigned int zdim) {
  unsigned off = floor(xyz.z)*ydim*xdim+floor(xyz.y)*xdim+floor(xyz.x);
  return off;
}

unsigned int makeKey(Voxel v, unsigned int xdim, unsigned int ydim, unsigned int zdim) {
  unsigned off = v.z*ydim*xdim+v.y*xdim+v.x;
  return off;
}

unsigned long long makeComboKey(unsigned int key1, unsigned int key2) {
  return (unsigned long long) key1 << 32 | key2;  /* We want keys in both order (symetric) */
  /*if (key1 < key2) {
    return (unsigned long long) key1 << 32 | key2;
  } else {
    return (unsigned long long) key2 << 32 | key1;
  }*/
}


int main (int argc, char **argv) {
  const char * ifname; 
  const char * ofname;

  int printStatus = 1;

  int count = -1;
  if (argc == 3) {
    ifname = argv[1];
    ofname = argv[2];
  } else if (argc == 4)  {
    ifname = argv[1];
    ofname = argv[2];
    count = atoi(argv[3]);
  } else {
    printf("Only 0, 1 or 2 arguments allowed\n");
    printf("%s <input> <output> [<fibers>]", argv[0]);
    return 1;
  }

  mode_t mask = S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH;


  printf("** Reading file %s...\n", ifname);
  int ifd;
  if ( (ifd = open(ifname, O_RDONLY | O_LARGEFILE)) == -1) {
    perror(ifname);
    return 1;
  }

  struct stFiberFileHeader header;
  read(ifd, &header, sizeof(struct stFiberFileHeader)); 

  if (strncmp(header.sFiberFileTag, "FiberDat", 8) != 0) {
    printf("Not a proper fiber-data file!");
    return 1;
  }

  printf("=== File Info ===\n");
  printf("= %d fibers; max-length %d; mean-length %f\n", header.nFiberNr, header.nFiberLenMax, header.fFiberLenMean);
  printf("= Image size: %dx%d(x%d)\n", header.nImgWidth, header.nImgHeight, header.nImgSlices);
  printf("= Voxel size: %fx%f(x%f)\n", header.fPixelSizeWidth, header.fPixelSizeHeight, header.fSliceThickness);
  printf("= Version: %8s\n", header.sVersion);
  printf("=== End Info ===\n");
  /* move file pointer 128, where fiber-data starts */
  lseek(ifd, 128, SEEK_SET);

  int xdim = header.nImgWidth;
  int ydim = header.nImgHeight;
  int zdim = header.nImgSlices;

  //vector<bool> covermap(xdim*ydim*zdim, false);
  vector<unsigned int> covermap(xdim*ydim*zdim, 0);

  //unsigned int *smap = new unsigned int [xdim*ydim*zdim];
  //unsigned int unused = 0xffffffff;
  //memset_pattern4(smap, &unused, sizeof(int)*xdim*ydim*zdim);


  /* Limit number of fibers (for testing) */
  if (count != -1) {
    printf("** Limiting input to %d fibers.\n", count);
    header.nFiberNr = count;
  }

  //set<unsigned long long> keys;
  map<unsigned long long, int> keys;
  
  int overlap = 0;

  struct Fiber fiber;
  /*float minx=0, miny=0, minz=0;
  float maxx=0, maxy=0, maxz=0; */
  for (int fn=0; fn < header.nFiberNr; fn++) {
    read(ifd, &(fiber.header), sizeof(fiber.header));
    //printf("Fiber %d has a length of %d.\n", i, fiber.header.nFiberLength);
    fiber.xyzFiberCoordinate = new XYZ_TRIPLE[fiber.header.nFiberLength];
    read(ifd, fiber.xyzFiberCoordinate, sizeof(XYZ_TRIPLE) * fiber.header.nFiberLength);

    /* print fibers */
    /*
    for (int j=0; j < fiber.header.nFiberLength; j++) {
      XYZ_TRIPLE xyz = fiber.xyzFiberCoordinate[j];
      printf("%d %f,%f,%f\n", j, xyz.x, xyz.y, xyz.z);
      if (j+1 < fiber.header.nFiberLength) {
         XYZ_TRIPLE xyz2 = fiber.xyzFiberCoordinate[j+1];
         printf("- %f,%f,%f\n", xyz2.x - xyz.x, xyz2.y - xyz.y, xyz2.z - xyz.z);
      }

    }*/

    /*
     * Find all voxels covered by this fiber
     */
    Voxel *voxels = new Voxel[fiber.header.nFiberLength];

    /*
    for (int j=0; j < fiber.header.nFiberLength; j++) {
      XYZ_TRIPLE xyz = fiber.xyzFiberCoordinate[j];
      if (fmodf(xyz.x, 1.0) == 0.0 && fmodf(xyz.y, 1.0) == 0.0 && fmodf(xyz.z, 1.0) == 0.0) {
        printf("%d %f,%f,%f\n", j, xyz.x, xyz.y, xyz.z);
      }
    }*/

    // find the origin
    int initial = -1;
    for (int j=0; j < fiber.header.nFiberLength; j++) {
      XYZ_TRIPLE xyz = fiber.xyzFiberCoordinate[j];
      if (fmodf(xyz.x, 1.0) == 0.5 && fmodf(xyz.y, 1.0) == 0.5  && fmodf(xyz.z, 1.0) == 0.5) {
        //printf("%d: %d is the start (of %d)\n", fn, j, fiber.header.nFiberLength);
        initial = j;
        voxels[initial] = Voxel((int) floor(xyz.x), (int) floor(xyz.y), (int) floor (xyz.z));
        break;
      }
    }
    
    // reverse
    for (int j=initial-1; j >= 0; j--) {
      XYZ_TRIPLE xyz = fiber.xyzFiberCoordinate[j];
      XYZ_TRIPLE xyz2 = fiber.xyzFiberCoordinate[j+1];
      Voxel v((int) floor(xyz.x), (int) floor(xyz.y), (int) floor (xyz.z));
      if (fmodf(xyz.x, 1.0) == 0.0 && (xyz.x - xyz2.x < 0.0)) {
        v.x -= 1;
      }
      if (fmodf(xyz.y, 1.0) == 0.0 && (xyz.y - xyz2.y < 0.0)) {
        v.y -= 1;
      }
      if (fmodf(xyz.z, 1.0) == 0.0 && (xyz.z - xyz2.z < 0.0)) {
        v.z -= 1;
      }
      voxels[j] = v;
    }

    // forward
    for (int j=initial+1; j < fiber.header.nFiberLength; j++) {
      XYZ_TRIPLE xyz = fiber.xyzFiberCoordinate[j];
      XYZ_TRIPLE xyz2 = fiber.xyzFiberCoordinate[j-1];
      Voxel v((int) floor(xyz.x), (int) floor(xyz.y), (int) floor (xyz.z));
      if (fmodf(xyz.x, 1.0) == 0.0 && (xyz.x - xyz2.x < 0.0)) {
        v.x -= 1;
      }
      if (fmodf(xyz.y, 1.0) == 0.0 && (xyz.y - xyz2.y < 0.0)) {
        v.y -= 1;
      }
      if (fmodf(xyz.z, 1.0) == 0.0 && (xyz.z - xyz2.z < 0.0)) {
        v.z -= 1;
      }
      voxels[j] = v;
    }

    /*for (int j=0; j < fiber.header.nFiberLength; j++) {
      printf("%d -- %d,%d,%d\n", j, voxels[j].x, voxels[j].y, voxels[j].z);
    }*/

    assert (initial >= 0);

    //printf("Thread %d\n", fn);

    bool found_overlap = false;

    set<unsigned long long> recordedKeys;
    for (int j=0; j < fiber.header.nFiberLength; j++) {
      //XYZ_TRIPLE xyz1 = fiber.xyzFiberCoordinate[j];
      unsigned int key1;
      //key1 = makeKey(xyz1,xdim,ydim,zdim);
      key1 = makeKey(voxels[j],xdim,ydim,zdim);
      covermap[key1] = 1;
      for (int k=j+1; k < fiber.header.nFiberLength; k++) {
        //XYZ_TRIPLE xyz2 = fiber.xyzFiberCoordinate[k];
        unsigned int key2;
        //key2 = makeKey(xyz2,xdim,ydim,zdim);
        key2 = makeKey(voxels[k],xdim,ydim,zdim);
        //printf("Found key %ld\n", makeComboKey(key1, key2));
        if (key1 == key2) {
          //printf("Found self\n");
          // skip identity
          if (!found_overlap)
              overlap++;
          found_overlap = true;
          continue;
        } 

        /* Make sure the lowest voxel comes first */
        map<unsigned long long, int>::iterator iter;
        unsigned long long comboKey;
        if (key1 < key2) {
          comboKey = makeComboKey(key1, key2);
        } else {
          comboKey = makeComboKey(key2, key1);
        }

        // Only count each key once per fiber! 
        if (recordedKeys.find(comboKey) != recordedKeys.end()) {
          continue;
        }

        iter = keys.find(comboKey);
        if (iter != keys.end()) {
          iter->second++;
        } else {
          keys[comboKey] = 1;
        }

        recordedKeys.insert(comboKey);

        /*iter = keys.find(makeComboKey(key1, key2));
        if (iter != keys.end()) {
          iter->second++;
        } else {
          keys[makeComboKey(key1, key2)] = 1;
        }*/
        /*
        iter = keys.find(makeComboKey(key2, key1));
        if (iter != keys.end()) {
          iter->second++;
        } else {
          keys[makeComboKey(key2, key1)] = 1;
        }*/


        //keys.insert(makeComboKey(key1, key2));
        //keys.insert(makeComboKey(key2, key1));



      /*if (fn == 0 && j == 0) {
         minx = maxx = xyz.x;
         miny = maxy = xyz.y;
         minz = maxz = xyz.z;
      }

      if (minx > xyz.x) { minx = xyz.x; }
      if (miny > xyz.y) { miny = xyz.y; }
      if (minz > xyz.z) { minz = xyz.z; }
      if (maxx < xyz.x) { maxx = xyz.x; }
      if (maxy < xyz.y) { maxy = xyz.y; }
      if (maxz < xyz.z) { maxz = xyz.z; }

      int x = floor(xyz.x);
      int y = floor(xyz.y);
      int z = floor(xyz.z); */
      //printf("%d,%d,%d\n", x,y,z);

      //int off = z*ydim*xdim+y*xdim+x;
      //smap[off] = i;

      //printf("%d: %f, %f, %f\n", j, fiber.xyzFiberCoordinate[j].x, fiber.xyzFiberCoordinate[j].y, fiber.xyzFiberCoordinate[j].z);
      }
    }
    delete [] fiber.xyzFiberCoordinate;
    delete [] voxels;
    fiber.xyzFiberCoordinate = NULL;

    if (printStatus) {
      if (fn % 500 == 499) { printf("."); };
      if (fn % 20000 == 19999) { printf(" %d\n", fn+1); };
    }
  }
  close (ifd);
  if (printStatus) { printf("\n"); };

  printf("\n=== %d self-overlapping fibers\n", overlap);

  char spatialname[255];
  snprintf(spatialname, sizeof(spatialname), "%s.spatial", ofname);
  printf("** Opening text format spatial output file %s...\n", spatialname);
  FILE *ofd = fopen(spatialname, "w");
  assert(ofd != NULL);
  fprintf(ofd, "n x y z\n");

  int voxelcount = 0;
  for (int n = 0; n < xdim*ydim*zdim; n++) {
    if (covermap[n]) {
      covermap[n] = voxelcount;
      fprintf(ofd, "%d %d %d %d\n", covermap[n], n % xdim, (n / xdim) % ydim, n / (xdim*ydim) );
      voxelcount++;
    }
  }
  printf("\n** %d voxels used\n", voxelcount);
  fclose(ofd);

  int nonzerovalues = keys.size() * 2;
  printf("** %d non-zero values\n", nonzerovalues);

  /*int count=0;
  for (int ii = 0; ii < xdim*ydim*zdim; ii++) { 
    if (smap[ii] != unused) {
      count++;
    }
  }
  printf("\n%d regions used.\n", count);
  */

  /*char smtfname[255];
  snprintf(smtfname, sizeof(smtfname), "%s.st", ofname);
  printf("** Opening text sparse matrix output file %s...\n", smtfname);
  ofd = fopen(smtfname, "w");
  assert(ofd != NULL);
  fprintf(ofd, "%d %d %d\n", voxelcount, voxelcount, nonzerovalues);*/

  char binarySparseFname[255];
  snprintf(binarySparseFname, sizeof(binarySparseFname), "%s.sb", ofname);
  printf("** Opening sparse binary matrix output file %s...\n", binarySparseFname);
  int sbfd;
  if ((sbfd = open(binarySparseFname, O_WRONLY | O_LARGEFILE | O_CREAT | O_TRUNC, mask)) == -1) {
    perror(binarySparseFname);
    exit(1);
  }

  // fprintf(ofd, "%d %d %d\n", voxelcount, voxelcount, nonzerovalues);
  // numRows numCols totalNonZeroValues
  write(sbfd, &voxelcount, sizeof(int));
  write(sbfd, &voxelcount, sizeof(int));
  write(sbfd, &nonzerovalues, sizeof(int));


  struct rowEntry {
    int id;
    float value;
  };

  /* Iterate through set to print out matrix for each voxel */
  unsigned int currentKey = 0xffffffff;
  //set<unsigned long long>::iterator it = keys.begin();
  map<unsigned long long,int>::iterator it = keys.begin();
  while (it != keys.end()) {
    //currentKey = *it >> 32;
    currentKey = it->first >> 32;
    map<unsigned int, unsigned int> dest;
    //while (currentKey == *it >> 32) {
    while (currentKey == it->first >> 32) {
      //unsigned int destKey = *it & 0xffffffff;
      unsigned int destKey = it->first & 0xffffffff;
      //dest.insert(destKey);
      dest[destKey] = it->second;
      //printf("Working on %X -> %X (%d -> %d)...\n", currentKey, destKey, covermap[currentKey], covermap[destKey]);

      /* If we are looking at the lowest voxel, we need to add the reverse edge */
      if (destKey > currentKey) {
        keys[makeComboKey(destKey, currentKey)] = it->second;
      }
      keys.erase(it++);
    }
    //fprintf(ofd, "%d\n", (int) dest.size());
    //for each column: numNonZeroValues
    int size = (int) dest.size();
    write(sbfd, &size, sizeof(int));
    struct rowEntry *rows = new struct rowEntry[size];
    int n = 0;
    for (map<unsigned int, unsigned int>::const_iterator dit = dest.begin(); dit!=dest.end(); ++dit) {
      //for each non-zero value in the column: rowIndex value
      //int id = covermap[*dit];
      //float value = 1.53;
      //write(sbfd, &id, sizeof(int));
      //write(sbfd, &value, sizeof(float));
      //fprintf(ofd, "%d 1\n", covermap[*dit]);
      rows[n].id = covermap[dit->first];
      rows[n].value = dit->second;
      n+=1;
    }
    write(sbfd, rows, sizeof(struct rowEntry)*size);
    delete [] rows;
  } 

  /* for (set<unsigned long long>::iterator it = keys.begin(); it!=keys.end(); ++it) {

      //printf("%llX\n", *it);
  } */


  fsync(sbfd);
  close(sbfd);

  printf("\n");
  //printf("X: %f-%f, Y: %f-%f, Z: %f-%f\n", minx, maxx, miny, maxy, minz, maxz);
  //printf("\n** Done.\n");

  /* just exit. no need to clean up after ourselves. */
  /* covermap.clear();
  keys.clear(); */

  return 0;
}
