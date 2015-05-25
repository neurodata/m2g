#!/bin/bash

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

# test_prog.sh
# Created by Disa Mhembere on 2015-01-29.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

set -e

DATA_DIR=./data
EXAMPLE_DIR=..
DJANGO_TOP=~/m2g/MR-OCP/MROCPdjango

echo "Starting django dev server ..."
python $DJANGO_TOP/manage.py runserver 8080 &
sleep 3

if [ ! -f $DATA_DIR/test_graph.graphml ]; then
  echo "Making test data .."
  mkdir $DATA_DIR
  Rscript test_graph.R
fi

echo "Running programmatic compute ..."
python $EXAMPLE_DIR/compute.py http://localhost:8080/graphupload \
  cc,tri,deg,mad,eig,ss1 $DATA_DIR/test_graph.graphml graphml
printf "\nSUCCESS!! Passed compute Test!!\n"

echo "Converting graph programmatically ..."
python $EXAMPLE_DIR/convert.py http://localhost:8080/convert/graphml/ncol,edgelist,lgl,pajek,dot,gml,leda $DATA_DIR/test_graph.graphml -l
printf "\nSUCCESS!! Passed compute Test!!\n"

echo "Building graph programmatically ..."
python $EXAMPLE_DIR/uploadsubj.py http://localhost:8080/upload/testproj/testsite/testsubj/testsesss/testscanID/s /data/MR.new/fiber/M87102806_fiber.dat 
printf "\nSUCCESS!! Passed build graph Test!!\n"

# cleanup
kill $(pgrep [p]ython)
rm -rf $DATA_DIR
