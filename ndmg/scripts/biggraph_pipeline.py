#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
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

# multigraph_pipeline.py
# Created by Greg Kiar and Will Gray Roncal on 2016-01-27.
# Email: gkiar@jhu.edu, wgr@jhu.edu

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE
import os.path as op
import nibabel as nb
from ndmg.graph import biggraph as mgg
import ndmg.utils as mgu
import numpy as np


def biggraphs(fibers, outdir):
    """
    Creates a brain graph from fiber streamlines
    """
    startTime = datetime.now()
    fiber_name = mgu.get_filename(fibers)
    base = fiber_name.split('_fibers', 1)[0]
    # Create output directories for graphs
    p = Popen("mkdir -p " + outdir + "/biggraphs/",
              stdout=PIPE, stderr=PIPE, shell=True)

    # Create names of files to be produced
    bgname = outdir + "/biggraphs/" + base + "_biggraph.csv"

    # Load fibers
    print "Loading fibers..."
    fiber_npz = np.load(fibers)
    tracks = fiber_npz[fiber_npz.keys()[0]]

    g1 = mgg()
    g1.make_graph(tracks)
    g1.save_graph(bgname)

    print "Execution took: " + str(datetime.now() - startTime)
    print "Complete!"
    pass


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("fibers", action="store", help="DTI streamlines")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p " + result.outdir + " " + result.outdir + "/tmp"
    print "Creating output directory: " + result.outdir
    print "Creating output temp directory: " + result.outdir + "/tmp"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()

    biggraphs(result.fibers, result.outdir)


if __name__ == "__main__":
    main()
