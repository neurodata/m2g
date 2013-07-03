#!/bin/bash
echo "Example downloads ./testdata directory from http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/ ..."
echo "Example script running ..."

if [ -f ./testdata/test_fiber.dat ]
then
  echo "./testdata/test_fiber.dat exists ..."
else
  if [ ! -d "$mkdir"];
  then
    echo "making testdata directory ..."
    mkdir ./testdata
  fi
  echo "downloading test_fiber.dat file..."
  wget --output-document=./testdata/test_fiber.dat http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_fiber.dat
fi

if [ -f ./testdata/test_roi.raw ]
then
  echo "./testdata/test_roi.raw exists ..."
else
  echo "downloading test_roi.raw file..."
  wget --output-document=./testdata/test_roi.raw http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.raw
fi

if [ -f ./testdata/test_roi.xml ]
then
  echo "./testdata/test_roi.xml exists ..."
else
  echo "downloading test_roi.xml file..."
  wget --output-document=./testdata/test_roi.xml http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.xml
fi


# SMALL
# Graph generation:
echo "../graph_exec -h. For help"
# Build a small graph given fiber streamline: test_fiber, fiber ROI's: test_roi.xml and test_roi.raw
.././graph_exec ./testdata/test_fiber.dat ./testdata/test_roi.xml ./testdata/test_roi.raw  -S ./testdata/small

# Invariants:
echo "./inv_exec -h. For help"
.././inv_exec ./testdata/small/test_fiber_70_smgr.mat -D fibergraph -A -S ./testdata/small

# largest connected component & single value:
echo "./deriv_exec -h. For help"
# Compute LCC & SVD
.././deriv_exec ./testdata/small/test_fiber_70_smgr.mat -v -l -S ./testdata/small

# BIG
# Uncomment to Build big graph WARNING: Can take up to 6 hours to complete
#.././graph_exec ./testdata/test_fiber.dat ./testdata/test_roi.xml ./testdata/test_roi.raw  -S ./testdata/big -b -g bigtest_bggr.mat

# largest connected component & single value:
#echo "./deriv_exec -h. For help"
# Compute LCC & SVD
#.././deriv_exec ./testdata/big/bigtest_bggr.mat -v -l -S ./testdata/big

# Invariants:
#echo "./inv_exec -h. For help"
#.././inv_exec ./testdata/big/bigtest_bggr.mat -D fibergraph -A -S ./testdata/big -lf ./testdata/big/LCC/bigtest_concomp.npy

