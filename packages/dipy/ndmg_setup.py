#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# m2g_startup.py
# Created by Greg Kiar on 2016-01-12.
# Email: gkiar@jhu.edu
# Copyright (c) 2016. All rights reserved

from argparse import ArgumentParser
import os
import sys
import glob


def setup(inDir, outputBaseDir, dtiListFile, bvalListFile, bvecListFile,
          mprageListFile, smgListFile, rdtiListFile, rmriListFile, bgListFile,
          tensorListFile, fiberListFile, atlasIn):

    # Create output directories
    outDirs = ['tensors', 'fibers', 'bg', 'graphs', 'reg_mprage', 'reg_dti']

    if not os.path.exists(outputBaseDir):
        os.makedirs(outputBaseDir)

    for f in outDirs:
        d = outputBaseDir + '/' + f
        if not os.path.exists(d):
            os.makedirs(d)

    atlasList = atlasIn

    # Create lists of files
    dti_types = ('*DTI.nii', '*DTI.nii.gz')
    dtiFiles = [y for x in os.walk(inDir) for z in dti_types
                for y in glob.glob(os.path.join(x[0], z))]

    bval_types = ('*.b', '*.bval')
    bvalFiles = [y for x in os.walk(inDir) for z in bval_types
                 for y in glob.glob(os.path.join(x[0], z))]

    bvec_types = ('*.bvec', '*.grad')
    bvecFiles = [y for x in os.walk(inDir) for z in bvec_types
                 for y in glob.glob(os.path.join(x[0], z))]

    mprage_types = ('*MPRAGE.nii', '*MPRAGE.nii.gz')
    mprageFiles = [y for x in os.walk(inDir) for z in mprage_types
                   for y in glob.glob(os.path.join(x[0], z))]

    # Writes lists to disk
    with open(dtiListFile, 'wb') as thefile:
        for item in dtiFiles:
            thefile.write("%s\n" % item)
    with open(bvalListFile, 'wb') as thefile:
        for item in bvalFiles:
            thefile.write("%s\n" % item)
    with open(bvecListFile, 'wb') as thefile:
        for item in bvecFiles:
            thefile.write("%s\n" % item)
    with open(mprageListFile, 'wb') as thefile:
        for item in mprageFiles:
            thefile.write("%s\n" % item)

    # Create graph list
    atlas = list()
    for a in atlasList:
        [xx, f] = os.path.split(a)
        [aa, xx] = os.path.splitext(os.path.splitext(f)[0])
        d = outputBaseDir + '/graphs/' + aa
        if not os.path.exists(d):
            os.makedirs(d)
        atlas.append(aa)

    sub = list()
    for s in dtiFiles:
        [xx, f] = os.path.split(s)
        [ss, xx] = os.path.splitext(os.path.splitext(f)[0])
        sub.append(ss.replace('DTI', ''))

    for f in outDirs:
        d = outputBaseDir + '/' + f
        if not os.path.exists(d):
            os.makedirs(d)

    # Output smg names
    smg = list()
    for s in sub:
        for a in atlas:
            smg.append(os.path.join(outputBaseDir + '/graphs/' +
                       a + '/' + s + a + '.graphml'))

    with open(smgListFile, 'wb') as thefile:
        for item in smg:
            thefile.write("%s\n" % item)

    # Create other derivative output lists
    rdtiName = list()
    rmriName = list()
    bgName = list()
    tensorName = list()
    fiberName = list()

    for s in sub:
        rdtiName.append(os.path.join(outputBaseDir, 'reg_dti',
                                     s + 'DTI_reg.nii.gz'))
        rmriName.append(os.path.join(outputBaseDir, 'reg_mprage',
                                     s + 'MPRAGE_reg.nii.gz'))
        bgName.append(os.path.join(outputBaseDir, 'bg',
                                   s + 'bg.graphml'))
        tensorName.append(os.path.join(outputBaseDir, 'tensors',
                                       s + 'tensors.Bdouble'))
        fiberName.append(os.path.join(outputBaseDir, 'fibers',
                                      s + 'fibers.dat'))

    # Save names to disk
    with open(rdtiListFile, 'wb') as thefile:
        for item in rdtiName:
            thefile.write("%s\n" % item)
    with open(rmriListFile, 'wb') as thefile:
        for item in rmriName:
            thefile.write("%s\n" % item)
    with open(bgListFile, 'wb') as thefile:
        for item in bgName:
            thefile.write("%s\n" % item)
    with open(tensorListFile, 'wb') as thefile:
        for item in tensorName:
            thefile.write("%s\n" % item)
    with open(fiberListFile, 'wb') as thefile:
        for item in fiberName:
            thefile.write("%s\n" % item)


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("inDir", action="store",
                        help="Input directory for raw data")
    parser.add_argument("outputBaseDir", action="store",
                        help="Output base directory for derivatives")
    parser.add_argument("dtiListFile", action="store", help="")
    parser.add_argument("bvalListFile", action="store", help="")
    parser.add_argument("bvecListFile", action="store", help="")
    parser.add_argument("mprageListFile", action="store", help="")
    parser.add_argument("smgListFile", action="store", help="")
    parser.add_argument("rdtiListFile", action="store", help="")
    parser.add_argument("rmriListFile", action="store", help="")
    parser.add_argument("bgListFile", action="store", help="")
    parser.add_argument("fiberListFile", action="store", help="")
    parser.add_argument("tensorListFile", action="store", help="")
    parser.add_argument("atlasIn", action="store", nargs="+", help="")
    result = parser.parse_args()

    setup(result.inDir, result.outputBaseDir, result.dtiListFile,
          result.bvalListFile, result.bvecListFile, result.mprageListFile,
          result.smgListFile, result.rdtiListFile, result.rmriListFile,
          result.bgListFile, result.tensorListFile, result.fiberListFile,
          result.atlasIn)

if __name__ == "__main__":
    main()
