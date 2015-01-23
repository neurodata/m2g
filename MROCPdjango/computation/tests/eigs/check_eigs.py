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

# check_eigs2.py
# Created by Disa Mhembere on 2014-01-20.
# Email: disa@jhu.edu

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