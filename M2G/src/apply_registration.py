#!/usr/bin/env python

# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

# apply_registration.py
# Created by Greg Kiar on 2015-02-26.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

# Load necessary packages
from os import system
from argparse import ArgumentParser


def apply_registration(original, warped, ref, tr):
    
    # Apply affine transformation
    system('antsApplyTransforms -d 3 -e 3 -t '+tr+' -i '+fixed+' -r '+ref+' -o '+warped)

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("original", action="store", help="Image that we are transforming (.nii, .nii.gz)")
  parser.add_argument("warped", action="store", help="Image that we are getting back (.nii, .nii.gz)")
  parser.add_argument("ref", action="store", help="Image we are registering to (.nii, .nii.gz)")
  parser.add_argument("tr", action="store", help="Transform matrix input (.mat)")
  
  result = parser.parse_args()

  apply_registration(result.original, result.warped, result.ref, result.tr)


if __name__ == "__main__":
  main()
