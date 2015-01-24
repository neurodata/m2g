#!/usr/bin/python

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

# transform_mux.py
# Created by Greg Kiar on 2015-01-19.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import scipy.io as sio
import numpy as np
import sys
import struct
import os

from contextlib import closing


def mux(translation1, rigid1, affine1):

  with closing(open(fiber_fn, "rb")) as fiber_f:
    file_size = os.fstat(fiber_f.fileno()).st_size

    for trans_fn in transforms:
      trans = sio.loadmat(trans_fn)["AffineTransform_double_3_3"]
      trans = np.reshape(trans, (3,4), order="F")
      
      count = 0
      while (fiber_f.tell() < file_size):
        fiber_header = np.fromfile(fiber_f, dtype=fiber_header_fmt, count=1)
        
        count += 1
        if count % 10000 == 0: print "%d fibers transformed ..." % count
        else:
          assert False, "Unknown fiber header format"

    print "Found %d fiber(s) of length > 1" % count

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("translation1", action="store", help="DTI-MPRAGE translation transform")
  parser.add_argument("rigid1", action="store", help="DTI-MPRAGE rigid transform")
  parser.add_argument("affine1", action="store", help="DTI-MPRAGE affine transform")
  parser.add_argument("outf", action="store", help="Output file for combined transform")
  result = parser.parse_args()

  mux(result.translation1, result.rigid1, result.affine1)

if __name__ == "__main__":
  main()
