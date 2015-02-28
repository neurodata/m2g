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
#

# sourceInstallRigraph.sh
# Created by Disa Mhembere on 2015-01-26.
# Email: disa@jhu.edu

set -e

if [ "$#" -ne 2 ]; then
  echo "Usage: sourceInstallRigraph cigraph_root_directory \
              rigraph_root_directory [install_location]"
  exit 1
fi

cd $1
./bootstrap.sh

if [ "$#" -eq 3 ]; then
  ./configure --prefix $3
else
  ./configure
fi
make

cd $2
git checkout dev
git submodule init
git submodule update
make

# Dependencies: irlba, NMF
R CMD INSTALL $(find . -name igraph_*-*)
