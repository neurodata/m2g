#!/bin/bash
echo "Example downloads ./testdata directory from http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/ ..."
mkdir ./testdata
cd testdata
wget http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_fiber.dat
wget http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.raw
wget http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.xml
cd ..

# Graph generation:
echo "../graph_exec -h. For help"
# Build a small graph given fiber streamline: test_fiber, fiber ROI's: test_roi.xml and test_roi.raw
.././graph_exec ./testdata/test_fiber.dat ./testdata/test_roi.xml ./testdata/test_roi.raw  -S ./testdata

# Invariants:
echo "./inv_exec -h. For help"
.././inv_exec ./testdata/test_fiber_70_smgr.mat s -D fibergraph -A -S ./testdata

# largest connected component & single value:
echo "./deriv_exec -h. For help"
# Compute LCC & SVD
.././deriv_exec ./testdata/test_fiber_70_smgr.mat -v -l -S ./testdata
