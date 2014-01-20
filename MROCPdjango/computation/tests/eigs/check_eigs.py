#!/usr/bin/python

# check_eigs2.py
# Created by Disa Mhembere on 2014-01-20.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.

# check the imaginary values of an eigenvector directory in .npy format

import os
from glob import glob
import sys
import numpy as np

assert len(sys.argv) > 1, "You must provide the directory name with eigenvector data .."

eigs = glob(os.path.join(sys.argv[1], "*.npy"))
count_nnz = []


for fh in eigs:
  print "Processing %s ..." % fh
  e = np.load(fh)
  #import pdb; pdb.set_trace()
  count_nnz.append(np.where(e.imag > 0)[0].shape[0])

fn = "/home/disa/count_nnz_eigs.npy"
np.save(fn, count_nnz)
print "Done"
