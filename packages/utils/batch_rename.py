#!/usr/bin/env python

# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

# batch_rename.py
# This file takes in a list file (text file with one filename (absolute path) per line
# Created by Will Gray Roncal on 2015-10-24.
# Email: wgr@jhu.edu
# Copyright (c) 2015. All rights reserved.

import os, sys
import glob
import shutil

# parse input files
inputNames = sys.argv[1]
inputFiles = sys.argv[2:]

# Read input names file    
with open(inputNames) as f:
    nameList = f.read().splitlines()

if len(inputFiles) != len(nameList):
    raise ValueError('Cannot rename - input file length output name lengths are different!')

else:
    for i in range(len(inputFiles)):
        print 'renaming file: '+inputFiles[i]+' to: '+nameList[i]
        shutil.rename(inputFiles[i],nameList[i])