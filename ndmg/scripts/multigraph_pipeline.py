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

from argparse import ArgumentParser
from datetime import datetime
from subprocess import Popen, PIPE
import os.path as op
import nibabel as nb
import ndmg.graph as mgg
import numpy as np


def multigraphs(fibers, labels, outdir):
    """
    Creates a brain graph from fiber streamlines
    """
    startTime = datetime.now()
    fiber_name = op.splitext(op.splitext(op.basename(fibers))[0])[0]
    base = fiber_name.split('_fibers', 1)[0]
    # Create output directories for graphs
    label_name = [op.splitext(op.splitext(op.basename(x))[0])[0]
                  for x in labels]
    for label in label_name:
        p = Popen("mkdir -p " + outdir + "/graphs/" + label,
                  stdout=PIPE, stderr=PIPE, shell=True)

    # Create names of files to be produced
    graphs = [outdir + "/graphs/" + x + '/' + base + "_" + x + ".graphml"
              for x in label_name]
    print "Graphs of streamlines downsampled to given labels: " +\
          (", ".join([x for x in graphs]))

    # Load fibers
    print "Loading fibers..."
    fiber_npz = np.load(fibers)
    tracks = fiber_npz[fiber_npz.keys()[0]]

    # Generate graphs from streamlines for each parcellation
    for idx, label in enumerate(label_name):
        print "Generating graph for " + label + " parcellation..."
        labels_im = nb.load(labels[idx])
        g1 = mgg(len(np.unique(labels_im.get_data()))-1, labels[idx])
        g1.make_graph(tracks)
        g1.summary()
        g1.save_graph(graphs[idx])

    print "Execution took: " + str(datetime.now() - startTime)
    print "Complete!"
    pass


def main():
    parser = ArgumentParser(description="This is an end-to-end connectome \
                            estimation pipeline from sMRI and DTI images")
    parser.add_argument("fibers", action="store", help="DTI streamlines")
    parser.add_argument("outdir", action="store", help="Path to which \
                        derivatives will be stored")
    parser.add_argument("labels", action="store", nargs="*", help="Nifti \
                        labels of regions of interest in atlas space")
    result = parser.parse_args()

    # Create output directory
    cmd = "mkdir -p " + result.outdir + " " + result.outdir + "/tmp"
    print "Creating output directory: " + result.outdir
    print "Creating output temp directory: " + result.outdir + "/tmp"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()

    multigraphs(result.fibers, result.labels, result.outdir)


if __name__ == "__main__":
    main()
