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

# setup.py
# Created by Disa Mhembere on 2015-04-15.
# Email: disa@jhu.edu

import argparse
import os
from subprocess import call
from webget import wget

__data_dir__ = os.path.join("./", ".data/")
weburl = "http://openconnecto.me/data/public/MR-data/"
__files__ = {
  "Atlas":[
  "desikan_in_mni_space/MNI152_T1_1mm_brain_incremented.nii",
  "desikan_in_mni_space/MNI152_T1_1mm_brain_labels_cropped.nii", 
  "desikan_in_mni_space/MNI152_T1_1mm_brain_mask.nii",
  "MNI152_T1_1mm_brain_labels.niiMNI152_T1_1mm_brain.nii",
  "m2g/MNI152_T1_1mm_brain.nii", "m2g/slab_atlas.nii", 
  "m2g/MNI152_T1_1mm_brain_incremented.nii"
  ], 
  "Centroids":["centroids.mat"], "Graphs": ["test.graphml"]
    }

def get_local_fn(fn, _type):
  os.path.join(os.path.join(__data_dir__, _type, os.path.basename(fn)))

def get_files():
  atlas_dir = os.path.join(__data_dir__, "Atlas")
  centroid_dir = os.path.join(__data_dir__, "Centroids")
  graphs_dir = os.path.join(__data_dir__, "Graphs")

  if not os.path.exists(atlas_dir):
    os.mkdir(atlas_dir)
  if not os.path.exists(centroid_dir):
    os.mkdir(centroid_dir)
  if not os.path.exists(graphs_dir):
    os.mkdir(graphs_dir)

  for k in __files__.keys():
    for v in __files__[k]:
      if not os.path.exists(get_local_fn(v, k)):
        wget(get_local_fn(v, k), weburl+k+"/"+v)

def compile_cython():
  os.chdir("../../MR-OCP/mrcap/")
  call(["python", "setup.py", "install"])

def main():
  parser = argparse.ArgumentParser(description="Compiles")
  result = parser.parse_args()


if __name__ == "__main__":
  main()
