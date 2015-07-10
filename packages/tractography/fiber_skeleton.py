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

# fiber_skeleton.py
# Based on fiber_convert.py (By Disa Mhembere)
# Created by Greg Kiar on 2015-06-29.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.


from argparse import ArgumentParser
from os import fstat 
from contextlib import closing
from numpy import dtype, fromfile
from mristudio_to_swc import SWC

headerFormat = dtype([('sFiberFileTag','a8'),
  ('nFiberNr','i4'), ('nFiberLenMax','i4'), ('fFiberLenMean','f4'),
  ('nImgWidth','i4'), ('nImgHeight','i4'), ('nImgSlices', 'i4'),
  ('fPixelSizeWidth','f4'), ('fPixelSizeHeight','f4'), ('fSliceThickness','f4'),
  ('enumSliceOrientation','i1'), ('enumSliceSequencing','i1'),
  ('sVersion','a8') ])
fiberHeaderFormat = dtype([('nFiberLength','i4'),
  ('cReserved', 'i1'),
  ('rgbFiberColor','3i1'),
  ('nSelectFiberStartPoint','i4'),
  ('nSelectFiberEndPoint','i4') ])
fiberDataFormat = dtype("3f4")


def offset(fiber_fn, swc_obj, fibers=0):
  """
  Converts fibers from Camino format to MRIStudio format
  
  Fibers produced by Camino are in a format which is incompatible with developed graph generation code, and thus are converted to the legacy MRIStudio format.
  
  **Positional Arguments**
  
  		MRIStudio fibers: [.dat; binary file]
  				- File generated containing fiber tracts computed from the diffusion tensors
  
  **Returns**
  
  		SWC fibers: [.swc; binary file]
  				- Output file containing the reformated fibers in a data format consistent with the SWC skeleton format.
  """
  with closing(open(fiber_fn, "rb")) as fiber_f:
  	#import pdb; pdb.set_trace()
  	file_size = fstat(fiber_f.fileno()).st_size
  	count=0
  	header = fromfile(fiber_f, dtype=headerFormat, count=1)
  	swc_obj.write_header(header[0], fiber_fn)
  	fiber_f.seek(128)
  	for i in range(0, header[0][1]):
  		fiber_header = fromfile(fiber_f, dtype=fiberHeaderFormat, count=1)
  		path = fromfile(fiber_f, dtype=fiberDataFormat, count=fiber_header[0][0])
  		count += 1
  		if count % 10000 == 0: print "%d fibers transformed ..." % count
  		swc_obj.write_path(path)
  		if count >= fibers and fibers > 0:
  			break

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("fiber_fn", action="store", help="fiber file")
  parser.add_argument("outfile", action="store", help="swc studio file")
  parser.add_argument("-n", "--fibers", type=int, default=0, help="number of fibers to process; 0 means all")
  result = parser.parse_args()

  offset(result.fiber_fn, SWC(result.outfile), result.fibers)

if __name__ == "__main__":
  main()
