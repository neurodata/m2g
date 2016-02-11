#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
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


def setup(inDir, dtiListFile, bvalListFile, bvecListFile, mprageListFile):
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


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("inDir", action="store",
                        help="Input directory for raw data")
    parser.add_argument("dtiListFile", action="store", help="")
    parser.add_argument("bvalListFile", action="store", help="")
    parser.add_argument("bvecListFile", action="store", help="")
    parser.add_argument("mprageListFile", action="store", help="")
    result = parser.parse_args()

    setup(result.inDir, result.dtiListFile, result.bvalListFile,
          result.bvecListFile, result.mprageListFile)

if __name__ == "__main__":
    main()
