
# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Disa Mhembere
# Email: disa@jhu.edu
#!/bin/bash
echo "Example downloads ./testdata directory from http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/ ..."
echo "Example script running ..."

# Exit script on first error
set -e 

# VAR DECL
TEST_DATA=./testdata
FIBER=$TEST_DATA/test_fiber.dat
ROI_XML=$TEST_DATA/test_roi.xml
ROI_RAW=$TEST_DATA/test_roi.raw
SMALL_DIR=$TEST_DATA/small
BIG_DIR=$TEST_DATA/big

SMALL_GR_FN=test_fiber_small.graphml
BIG_GR_FN=test_fiber_big.graphml

if [ ! -d $TEST_DATA ]
then
  echo "making $TEST_DATA directory ..."
  mkdir $TEST_DATA
fi

if [ -f $FIBER ]
then
  echo "$FIBER exists ..."
else
  echo "Downloading $FIBER file..."
  wget --output-document=$FIBER http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_fiber.dat
fi

if [ -f $ROI_RAW ]
then
  echo "$ROI_RAW exists ..."
else
  echo "Downloading $ROI_RAW file..."
  wget --output-document=$ROI_RAW http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.raw
fi

if [ -f $ROI_XML ]
then
  echo "$ROI_XML exists ..."
else
  echo "Downloading $ROI_XML file..."
  wget --output-document=$ROI_XML http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.xml
fi

# BIG
# Uncomment to Build big graph WARNING: Can take up to 2 hours to complete
if [[ $1 == "-b" ]]; then
  python ../graph_exec $FIBER $ROI_XML $ROI_RAW -S $BIG_DIR -b -g $BIG_GR_FN -a ../../../../mrcap/utils/desikan_atlas.nii,$(readlink -f $(pwd)/../../../..)/mrcap/utils/desikan_atlas.txt ../../../../mrcap/utils/20k_atlas.nii

  # Invariants:
  echo "./inv_exec -h. For help"
  python .././inv_exec $BIG_DIR/$BIG_GR_FN -A -S $BIG_DIR 
  exit
else
  echo 'To build a big graph pass -b as the 1 argument to the example script'
fi

# SMALL
# Graph generation:
echo "../graph_exec -h. For help"
# Build a small graph given fiber streamline: test_fiber, fiber ROI's: test_roi.xml and test_roi.raw
python ../graph_exec $FIBER $ROI_XML $ROI_RAW -S $SMALL_DIR -g $SMALL_GR_FN -a ../../../../mrcap/utils/desikan_atlas.nii

# Invariants:
echo "./inv_exec -h. For help"
python ../inv_exec $SMALL_DIR/$SMALL_GR_FN -A -S $SMALL_DIR 
