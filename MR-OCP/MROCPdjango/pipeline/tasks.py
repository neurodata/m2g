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

# tasks.py
# Created by Disa Mhembere on 2015-09-06.
# Email: disa@jhu.edu

from __future__ import absolute_import

from celery import task
from django.conf import settings

#import logging
#logger = logging.getLogger("mrocp")

@task(queue='mrocp')
def mrocp(param):
  print "The param was {0}!!!".format(param)
  return "EXITED CORRECTLY"

@task(queue="mrocp")
def task_convert(media_root, upload_fn, convert_file_save_loc, 
                                input_format, output_format, to_email):
  print "Entering convert task ..."
  from pipeline.procs.convert import convert
  convert(media_root, upload_fn,convert_file_save_loc,  input_format, output_format, to_email) 
  print "Exiting convert task ..."

@task(queue="mrocp")
def task_invariant_compute(invariants, graph_fn, invariants_path, 
                                            data_dir, in_graph_format, to_email):
  print "Entering invariant task ..."
  from pipeline.procs.inv_compute import invariant_compute
  invariant_compute(invariants, graph_fn, invariants_path, 
        data_dir, in_graph_format, to_email)
  print "Exiting invariant task ..."

@task(queue="mrocp")
def task_runc4(dti_path, mprage_path, bvalue_path, bvector_path, graph_size, atlas, email):
  print "Entering c4 task ..."
  from pipeline.procs.runc4 import runc4
  runc4(dti_path, mprage_path, bvalue_path, bvector_path, graph_size, atlas, email)
  print "Exiting c4 task ..."

@task(queue="mrocp")
def task_build():
  print "Entering build task ..."
  #TODO
  print "Exiting build task ..."

@task(queue="mrocp")
def task_scale(selected_files, dl_format, ds_factor, ATLASES, email=None, dwnld_loc=None, zip_fn=None):
  from pipeline.procs.scale_convert import scale_convert
  print "Entering download task ..."
  scale_convert(selected_files, dl_format, ds_factor, ATLASES, email, dwnld_loc, zip_fn)
  print "Exiting download task ..."
