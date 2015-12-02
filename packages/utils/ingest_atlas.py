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
import matplotlib.pyplot as plt
from argparse import ArgumentParser

def ingest(raw, ingested, template, qc=False):
  
  template_im = nb.load(template)
  raw_im = nb.load(raw)
  
  ingested_im = nl.resample_img(raw_im, target_affine=template_im.get_affine(), target_shape=template_im.get_data().shape, interpolation='nearest')
  
  nb.save(ingested_im, ingested)
  
  print "here"
  if qc:
    print "here 2"
    t = template_im.get_data()
    dim1 = t.shape
    r = raw_im.get_data()
    dim2 = r.shape
    i = ingested_im.get_data()
    dim3 = i.shape
    name = os.path.splitext(os.path.splitext(ingested)[0])[0]+'_QC.png'
    print name
    show_slices([ t[dim1[0]/2,:,:], t[:,dim1[1]/2,:], t[:,:,dim1[2]/2] ],
                [ r[dim2[0]/2,:,:], r[:,dim2[1]/2,:], r[:,:,dim2[2]/2] ],
                [ i[dim3[0]/2,:,:], i[:,dim3[1]/2,:], i[:,:,dim3[2]/2] ],
                name)


def show_slices(template, raw, ing, name):
  assert(len(template) == len(raw))
  assert(len(template) == len(ing))
  dmax = np.max([raw[0].max(), raw[1].max(), raw[2].max()])
  fig, axes = plt.subplots(1, len(template))
  for i, temp in enumerate(template):
    axes[i].imshow(template[i].T, cmap="Greys", origin="lower")
    axes[i].hold(True)
    axes[i].imshow(raw[i].T, cmap="cool", alpha=0.7, origin="lower", vmin=1, vmax=dmax)
    axes[i].imshow(ing[i].T, cmap="Set1", alpha=0.7, origin="lower", vmin=1, vmax=dmax)
  fig.savefig(name)


def main():
  parser = ArgumentParser(description="Transforms an atlas from original space into template space")
  parser.add_argument("raw", action="store", help="The un-ingested atlas labels")
  parser.add_argument("ingested", action="store", help="The ingested atlas labels output location")
  parser.add_argument("template", action="store", help="The template space to which you are ingesting")
  parser.add_argument("--qc", "-q", action="store_true", default=False, help="Flag indicating whether or not you want QC")
  result = parser.parse_args()

  ingest(result.raw, result.ingested, result.template, result.qc)

if __name__ == "__main__":
  main()
