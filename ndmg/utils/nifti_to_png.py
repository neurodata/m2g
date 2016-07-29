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

# nifti_to_png.py
# Created by Greg Kiar on 2016-06-13.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
from scipy.misc import imsave
import nibabel as nb
import os


def convert(indir, outdir,  verbose=False):
    """
    Takes in nifti images, creates directory structure desired by ndstore
    ingest, and then converts niftis to png stacks. This script should be
    called prior to ingesting MR data into ndstore.
    """

    # Create output directory structure
    if verbose:
        print "Creating", outdir, "..."
    os.system('mkdir -p '+outdir)

    for path, dirs, files in os.walk(indir):
        for idx, fl in enumerate(files):
            if verbose:
                print "Loading subject to learn number of time points..."
            im = nb.load(path+fl)
            dat = im.get_data()
            ntime = dat.shape[3]

            base = os.path.splitext(os.path.splitext(fl)[0])[0]
            chan = "_".join(base.split('_')[1:3])
            if verbose:
                print "File:", fl
                print "Channel:", chan
                print "Time steps:", ntime
                print "Creating", outdir + "/" + chan, "..."
            os.system('mkdir -p ' + outdir + "/" + chan)

            for count in range(int(ntime)):
                dirname = outdir + "/" + chan + "/time%04d" % count
                if verbose:
                    print "Creating", dirname, "..."
                os.system('mkdir -p ' + dirname)
                for slices in range(dat.shape[2]):
                    if verbose:
                        print "Saving slice:", slices
                    imsave(dirname + '/%04d.png' % slices,
                           dat[:, :, slices, count].astype('float32').T)


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("indir", action="store", help="directory for niftis")
    parser.add_argument("outdir",  action="store", help="directory for pngs")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Toggles output text")
    result = parser.parse_args()

    convert(result.indir, result.outdir, result.verbose)


if __name__ == "__main__":
    main()
