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

# m2g_setup.py
# Created by Will Gray Roncal on 2015-10-24.
# Email: wgr@jhu.edu
# Copyright (c) 2015. All rights reserved.

import os, sys
import glob

# parse input files
inDir = sys.argv[1]
outputBaseDir = sys.argv[2]
atlasIn = sys.argv[3]

dtiListFile = sys.argv[4]
bvalListFile = sys.argv[5]
bvecListFile = sys.argv[6]
mprageListFile = sys.argv[7]
atlasListFile = sys.argv[8]

#make output directory and subdirectories
outDirs = ['fibers', 'graphs', 'registered']

if not os.path.exists(outputBaseDir):
    os.makedirs(outputBaseDir)
    
for f in outDirs:
    d = outputBaseDir + '/' + f
    if not os.path.exists(d):
        os.makedirs(d)

# Read atlas file    
with open(atlasIn) as f:
    atlasList = f.read().splitlines()
    
#save list of paths as csvs

dtiFiles = [y for x in os.walk(inDir) for y in glob.glob(os.path.join(x[0], '*DTI.nii'))]
bvalFiles = [y for x in os.walk(inDir) for y in glob.glob(os.path.join(x[0], '*.b'))]
bvecFiles = [y for x in os.walk(inDir) for y in glob.glob(os.path.join(x[0], '*.grad'))]
mprageFiles = [y for x in os.walk(inDir) for y in glob.glob(os.path.join(x[0], '*MPRAGE.nii'))]

with open(dtiListFile,'wb') as thefile:
    for item in dtiFiles:
        thefile.write("%s\n" % item)
        
with open(bvalListFile,'wb') as thefile:
    for item in bvalFiles:
        thefile.write("%s\n" % item)

with open(bvecListFile,'wb') as thefile:
    for item in bvecFiles:
        thefile.write("%s\n" % item)

with open(mprageListFile,'wb') as thefile:
    for item in mprageFiles:
        thefile.write("%s\n" % item)

#construct small graph stuff

atlas = list()
for a in atlasList:
    [xx, f] = os.path.split(a)
    [aa, xx]  = os.path.splitext(f)
    atlas.append(aa)
    
sub = list()
for s in dtiFiles:
    [xx, f] = os.path.split(s)
    [ss, xx]  = os.path.splitext(f)
    sub.append(ss.replace('DTI',''))

print sub
print atlas    

# output smg names

smg = list()
for s in sub:
    for a in atlas:
       smg.append(s+a+'_sg.graphml')
       
print smg


with open(atlasListFile,'wb') as thefile:
    for item in smg:
        thefile.write("%s\n" % item)