
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

#!/bin/bash

# test_inv.sh
# Created by Disa Mhembere on 2014-08-13.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

echo "Testing invariants ..."
GRAPH_FN="./mrdata/graphs/test.graphml"

set -e

./inv_exec -h
echo "Testing All ..."
./inv_exec $GRAPH_FN -A
echo; echo # crappy way to skip two lines

echo "Testing individuals ..."
./inv_exec $GRAPH_FN -d
./inv_exec $GRAPH_FN -e
./inv_exec $GRAPH_FN -c
./inv_exec $GRAPH_FN -t
./inv_exec $GRAPH_FN -s
./inv_exec $GRAPH_FN -m
./inv_exec $GRAPH_FN -g
./inv_exec $GRAPH_FN -v
