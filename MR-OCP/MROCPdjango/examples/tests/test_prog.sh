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

if [ "$#" -ne 1 ]; then
  echo "usage: ./test_prog.sh <email_address>"
  exit 911
fi

EMAIL=$1
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

<<COMMENT
echo "Running programmatic compute ..."
python $EXAMPLE_DIR/compute.py http://localhost:8080/graph-services/graphupload \
  $DATA_DIR/test_graph.graphml $EMAIL graphml -i cc tri deg mad eig ss1
printf "\n Completed compute Test. If failed -- html source will print\n"

echo "Converting graph programmatically ..."
python $EXAMPLE_DIR/convert.py http://localhost:8080/graph-services/convert \
  $DATA_DIR/test_graph.graphml $EMAIL -i graphml -o ncol,edgelist,lgl,pajek,dot,gml,leda -l
printf "\n Completed convert Test. If failed -- html source will print\n"
COMMENT

echo "Building graph programmatically ..."
python $EXAMPLE_DIR/buildsubj.py http://localhost:8080/graph-services/buildgraph/testproj/testsite/testsubj/testsesss/testscanID/s \
  /data/MR.new/fiber/M87102806_fiber.dat $EMAIL -i deg 
printf "\nSUCCESS!! Passed build graph Test!!\n"

# cleanup
kill $(pgrep [p]ython) || true
kill $(pgrep [P]ython) || true
rm -rf $DATA_DIR
