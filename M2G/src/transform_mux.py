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


def mux(transforms, outf):

  h = np.matrix(( (1,0,0,0), (0,1,0,0), (0,0,1,0) ))
  for trans in transforms:
    t = np.reshape(sio.loadmat(trans)["AffineTransform_double_3_3"], (3,4), order="F")
    h = np.dot(np.transpose(t[0:3,0:3]), h) + np.matrix(( (0,0,0,t[0,3]), (0,0,0,t[1,3]), (0,0,0,t[2,3]) ))
  
  h = np.reshape(h, (12,1), order="F")
  mdict = {"AffineTransform_double_3_3": h, "fixed": [0, 0, 0]}
  sio.savemat(outf, mdict)
  

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("outf", action="store", help="Output file for combined transform")
  parser.add_argument("-t", "--transforms", nargs="+", help="Some transform")
  result = parser.parse_args()

  mux(result.transforms, result.outf)

if __name__ == "__main__":
  main()
