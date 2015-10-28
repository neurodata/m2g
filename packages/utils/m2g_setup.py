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

# input list files
dtiListFile = sys.argv[4]
bvalListFile = sys.argv[5]
bvecListFile = sys.argv[6]
mprageListFile = sys.argv[7]

# output list files
#Registred DTI data, registered mprage data, sg, bg, fibers

smgListFile = os.path.join(outputBaseDir,'sgListFile.list') #sys.argv[8]
rdtiListFile = os.path.join(outputBaseDir,'rdtiListFile.list')#sys.argv[9]
rmriListFile = os.path.join(outputBaseDir,'rmriListFile.list')#sys.argv[10]
bgListFile = os.path.join(outputBaseDir,'bgListFile.list')#sys.argv[11]
fiberListFile = os.path.join(outputBaseDir,'fiberListFile.list')#sys.argv[12]

#make output directory and subdirectories
outDirs = ['fibers', 'sg', 'bg', 'reg']

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

# DTI in
with open(dtiListFile,'wb') as thefile:
    for item in dtiFiles:
        thefile.write("%s\n" % item)

# bval in                                
with open(bvalListFile,'wb') as thefile:
    for item in bvalFiles:
        thefile.write("%s\n" % item)

# bvec in
with open(bvecListFile,'wb') as thefile:
    for item in bvecFiles:
        thefile.write("%s\n" % item)

# mprage in
with open(mprageListFile,'wb') as thefile:
    for item in mprageFiles:
        thefile.write("%s\n" % item)

#construct small graph filenames - done differently because of combinatorics

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

# output smg names

smg = list()
for s in sub:
    for a in atlas:
       smg.append(outputBaseDir + 'sg' + s + a + '_sg.graphml')

print sub
print atlas    
print smg

with open(smgListFile,'wb') as thefile:
    for item in smg:
        thefile.write("%s\n" % item)
        
# sub is the base subject directory 
rdtiName = list()
rmriName = list()
bgName = list()
fiberName = list()
       
for s in sub:
    rdtiName.append(os.path.join(outputBaseDir, 'reg', s + 'dti_reg.nii'))
    rmriName.append(os.path.join(outputBaseDir, 'reg', s + 'mprage_reg.nii'))
    bgName.append(os.path.join(outputBaseDir, 'bg', s + 'bg.graphml'))
    fiberName.append(os.path.join(outputBaseDir, 'fiber', s + 'fiber.dat'))

# registered dti names
with open(rdtiListFile,'wb') as thefile:
    for item in rdtiName:
        thefile.write("%s\n" % item)

# registered mprage names
with open(rmriListFile,'wb') as thefile:
    for item in rmriName:
        thefile.write("%s\n" % item)

# bg names
with open(bgListFile,'wb') as thefile:
    for item in bgName:
        thefile.write("%s\n" % item)

# fiber names
with open(fiberListFile,'wb') as thefile:
    for item in fiberName:
        thefile.write("%s\n" % item)