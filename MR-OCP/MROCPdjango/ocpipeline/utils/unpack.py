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

# unpack.py
# Created by Disa Mhembere on 2014-06-09.
# Email: disa@jhu.edu

import argparse
from glob import glob
import os
import zipfile
import subprocess
import shutil

def unpack(base_dir):

  for _file_ in glob(os.path.join(base_dir,"*")):
    out = subprocess.check_output(["unzip", _file_])
    print out
    os.remove(_file_) # remove old zip
    graph_fn = out.splitlines()[1].split(":")[1].strip()
    if base_dir == "/mnt/bg1publicdata/graphs/.migraine-v2/NKI-TRT_MIGRAINE_v1_0_2_2014-05-31/big_graphs/":
      print "Adapting file name ..."
      graph_fn = "NKI-TRT"+graph_fn[6:] 

    subprocess.call(["zip","-j", "-v", _file_, graph_fn])
    shutil.rmtree(graph_fn.split("/")[0]) # remove uncompressed graph file

  print "Done!"


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("base_dir", action="store", help="The base directory with files")
  result = parser.parse_args()
  
  unpack(result.base_dir)

if __name__ == "__main__":
  main()
