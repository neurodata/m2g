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
def mrocp():
  """Propagate the given project for all resolutions"""
  print "I have arrived!!!"
  return "EXITED CORRECTLY"
