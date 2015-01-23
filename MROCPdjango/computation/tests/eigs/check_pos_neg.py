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

# check_pos_neg2.py
# Created by Disa Mhembere on 2014-01-20.
# Email: disa@jhu.edu

# Check the distribution of positive/negative real values of eigenvectors in a directory (.npy format)

import os
from glob import glob
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import pylab as pl

assert len(sys.argv) > 1, "You must provide the directory name with eigenvector data .."

eigs = glob(os.path.join(sys.argv[1], "*_eigvl.npy"))
all_eigvals = np.array([])

for eigfn in eigs:
  print "Processing %s ..." % eigfn
  e = np.load(eigfn)

  for eigval in e:
    all_eigvals = np.append(all_eigvals, eigval.real)

pl.figure(1)
n, bins, patches = pl.hist(all_eigvals, bins=100 , range=None, normed=False, weights=None, cumulative=False, \
       bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
       rwidth=None, log=False, color=None, label=None, hold=None)

fn = "/home/disa/dist_nnz_eigs.pdf"
pl.savefig(fn)
print "Done"