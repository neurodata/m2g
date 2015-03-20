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

# cpac_list_gen.py
# Created by Greg Kiar on 2015-03-29.
# Email: gkiar@jhu.edu
# Copyright (c) 2015. All rights reserved.

from argparse import ArgumentParser
from os import listdir
from os.path import isdir, join
from re import compile, sub
from random import random
from numpy import floor

def make_list(datadir, template, outlist):
  
  inf = open(template, 'r')
  content = inf.readlines()
  inf.close()

  p = compile('num|path')
  dirs = [f for f in listdir(datadir) if isdir(join(datadir,f))]
  out_data = list()
  for i in range(0, len(dirs)):
    temp_sub =  content[:]
    
    subj_id = i+1
    unique_id = floor(random()*pow(2,32))
    mprage_path = join(datadir, dirs[i]+'/'+dirs[i]+'-MPRAGE.nii')
    fmri_path = join(datadir, dirs[i]+'/'+dirs[i]+'-fMRI.nii')

    temp_sub[1] = p.sub("'"+str(subj_id)+"'", temp_sub[1])
    temp_sub[2] = p.sub("'"+str(int(unique_id))+"'", temp_sub[2])
    temp_sub[3] = p.sub("'"+mprage_path+"'", temp_sub[3])
    temp_sub[4] = p.sub("'"+fmri_path+"'", temp_sub[4])
    out_data.append(temp_sub)
  
  ouf = open(outlist, 'w')
  for subj in out_data:
    for val in subj:
      ouf.write(val)
  ouf.close()

def main():
  parser = ArgumentParser(description="")
  parser.add_argument("data_dir", action="store", help="base data directory (contains directories for all subjects")
  parser.add_argument("outlist", action="store", help="output list file")
  parser.add_argument("-t","--template", nargs="+", help="template for cpac format")

  result = parser.parse_args()
  if result.template:
    make_list(result.data_dir, result.template, result.outlist)
  else:
    make_list(result.data_dir, 'template_for_cpac.yml', result.outlist)

if __name__=='__main__':
  main()
