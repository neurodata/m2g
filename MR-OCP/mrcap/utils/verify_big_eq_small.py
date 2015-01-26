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

# verify_big_eq_small.py
# Created by Disa Mhembere on 2014-07-15.
# Email: disa@jhu.edu
# Used in a verification step to ensure the big graphs and small graphs
# provide equivalent representations when the big is scaled down.

import argparse
from downsample import downsample
import igraph_io
import os
from mrcap.atlas import Atlas

def verify(gsmall, gbig, atlas):
 gbig = downsample(gbig, atlas=atlas) # gbig has been downsampled
 assert ds_big.get_adjacency() == gsmall.get_adjacency(), "Adjacency matrices unequal!"
 assert gbig.es["weight"] == gsmall.es["weight"], "Adjacency matrix weights unequal!"

def main():
  parser = argparse.ArgumentParser(description="Verify that given a big graph I can\
      obtain the equivalent small graph")
  parser.add_argument("biggfn", action="store", help="The big graph filename")
  parser.add_argument("--b", "--bigformat", default="graphml", help="The format of\
      the big graph")
  parser.add_argument("smallgfn", action="store", help="The small graph filename")
  parser.add_argument("--s", "--smallformat", default="graphml", help="The format\
      of the small graph")
  parser.add_argument("-a", "--atlasfn", action="store", default=os.path.join(
    os.path.dirname(__file__), "desikan_atlas.nii") ,help="The desikan atlas filename")

  result = parser.parse_args()

  gsmall = igraph_io.read_arbitrary(result.smallgfn, result.smallformat)
  gbig = igraph_io.read_arbitrary(result.biggfn, result.bigformat)
  atlas = Atlas(result.atlasfn)

  verify(gsmall, gbig, atlas)

if __name__ == "__main__":
  main()
