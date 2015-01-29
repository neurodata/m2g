#!/usr/bin/env python

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

# test_camino_to_mristudio.py
# Created by Disa Mhembere on 2015-01-13.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

# Mini-test
from mrcap.fiber import FiberReader
import sys
import os

if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
  sys.stderr.write("Pass in a MRI studio fiber file\n")
  exit(0) # for friendly exit

reader = FiberReader(sys.argv[1])
reader.shape = (182, 218, 182)
reader.fiberCount = 30000

print "Reader Header", reader

for fiber in reader:
  print fiber
