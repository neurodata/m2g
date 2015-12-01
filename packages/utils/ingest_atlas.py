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

# ingest_atlas.py
# Created by Greg Kiar on 2015-12-01.
# Email: gkiar@jhu.edu

import nilearn.image as nl
import nibabel as nb
import numpy as np
import os
from argparse import ArgumentParser

def ingest(raw, ingested, template, noaff, qc=False):
  
  template_im = nb.load(template)
  raw_im = nb.load(raw)
  if qc:
    #TODO print coronal slice in real space, and image space, overlaid on template
    pass

  ingested_im = nl.resample_img(raw_im, target_affine=template_im.get_affine(), target_shape=template_im.get_data().shape, interpolation='nearest')
  if qc:
    #TODO print coronal slice in real space, and image space, overlaid on template
    pass

  nb.save(ingested_im, ingested)
  ingested_noaff = nb.Nifti1Image(ingested_im.get_data(), affine=np.eye(4), header=ingested_im.get_header())
  if qc:
    #TODO print coronal slice in real space, and image space, overlaid on template
    pass

  nb.save(ingested_noaff, noaff)
 

def main():
  parser = ArgumentParser(description="Transforms an atlas from original space into template space")
  parser.add_argument("raw", action="store", help="The un-ingested atlas labels")
  parser.add_argument("ingested", action="store", help="The ingested atlas labels output location")
  parser.add_argument("template", action="store", help="The template space to which you are ingesting")
  parser.add_argument("-q","--qc", action="store", type=bool, help="Flag indicating whether or not you want qc")
  result = parser.parse_args()

  #Strips extension (twice in case .nii.gz) and creates noaff file name
  noaff = os.path.splitext(os.path.splitext(result.ingested)[0])[0]+'_noaff.nii.gz'

  ingest(result.raw, result.ingested, result.template, noaff, result.qc)

if __name__ == "__main__":
  main()
