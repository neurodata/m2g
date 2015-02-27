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

# fiber_convert.py
# Created by Disa Mhembere on 2015-01-13.
# Modified by Greg Kiar on 2015-02-26.
# Email: disa@jhu.edu
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from argparse import ArgumentParser
import scipy.io as sio
import numpy as np
import sys
import struct
import os
from os import fstat 
from contextlib import closing
from numpy import dtype, fromfile
from camino_to_mristudio import MRIstudio

fiber_header_fmt = dtype([('nFiberLength','>f4'), ('nSelectFiberStartPoint','>f4')])
fiber_data_fmt = dtype(">3f4")

def offset(fiber_fn, mristudio_obj):

  with closing(open(fiber_fn, "rb")) as fiber_f:
    file_size = fstat(fiber_f.fileno()).st_size
    count = 0
    while (fiber_f.tell() < file_size):
      fiber_header = fromfile(fiber_f, dtype=fiber_header_fmt, count=1)
      if fiber_header[0][0] == 1:
        fiber_f.seek(fiber_f.tell()+12) # Just skip ahead to account for 1-length 
      elif fiber_header[0][0] > 1:
        path = fromfile(fiber_f, dtype=fiber_data_fmt, count=fiber_header[0][0])
        mristudio_obj.write_path(path)
        count += 1
        if count % 10000 == 0: print "%d fibers transformed ..." % count
      else:
        assert False, "Unknown fiber header format"
    print "Found %d fiber(s) of length > 1" % count
    mristudio_obj.set_num_fibers(count) # For fiber header

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("fiber_fn", action="store", help="fiber file")
  parser.add_argument("outfile", action="store", help="mri studio file")
  result = parser.parse_args()

  offset(result.fiber_fn, MRIstudio(result.outfile))

if __name__ == "__main__":
  main()
