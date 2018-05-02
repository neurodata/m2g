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

    dtiFiles = get_files(dti_types, inDir)

    bval_types = ('*.b', '*.bval')
    bvalFiles = get_files(bval_types, inDir)

    bvec_types = ('*.bvec', '*.grad')
    bvecFiles = get_files(bvec_types, inDir)

    mprage_types = ('*MPRAGE.nii', '*MPRAGE.nii.gz')
    mprageFiles = get_files(mprage_types, inDir)

    # Writes lists to disk
    write_files(dtiListFile, dtiFiles)
    write_files(bvalListFile, bvalFiles)
    write_files(bvecListFile, bvecFiles)
    write_files(mprageListFile, mprageFiles)


def get_files(ftypes, inDir):
    return [y for x in os.walk(inDir) for z in ftypes
            for y in glob.glob(os.path.join(x[0], z))]


def write_files(outfile, filelist):
    with open(outfile, 'wb') as thefile:
        for item in filelist:
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
