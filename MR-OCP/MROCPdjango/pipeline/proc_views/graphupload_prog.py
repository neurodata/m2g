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

# graphupload_prog.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

from glob import glob
import os
from time import strftime, localtime

from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings

from pipeline.utils.util import makeDirIfNone, writeBodyToDisk, saveFileToDisk
from pipeline.utils.util import sendJobBeginEmail
from pipeline.procs.inv_compute import invariant_compute
from pipeline.utils.zipper import unzip 
from pipeline.procs.run_invariants import run_invariants
from pipeline.tasks import task_invariant_compute
from pipeline.utils.util import get_script_prefix
import re

# Simple email address test
def check_email(email):
  patt = re.compile("[^@]+@[^@]+\.[^@]+")
  if (re.match(patt, email)):
    return True
  return False

def graph_load_inv_prog(request, webargs=None):
  if request.method == 'POST' and webargs:

    split_webargs = webargs.split("/")
    to_email = split_webargs[0]
    if (not check_email(to_email)):
      return HttpResponse("ERROR: Incorrect email address format")

    try:
      in_graph_format = split_webargs[1]
      if in_graph_format not in ("graphml", "ncol", "edgelist", "lgl", "pajek", "graphdb", "numpy", "mat"):
        return HttpResponse("ERROR: Unknown graph input format")
      invariants = split_webargs[2:]
      if not invariants: 
        return HttpResponse("ERROR: No invariants to compute provided")
    except:
      return HttpResponse("ERROR: Error with input graph format OR invariants chosen")

    data_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
    makeDirIfNone([data_dir])
    uploadedZip = writeBodyToDisk(request.body, data_dir)[0] # Not necessarily a zip

    try: # Assume its a zip first
      unzip(uploadedZip, data_dir) # Unzip the zip
      os.remove(uploadedZip) # Delete the zip
    except:
      print "Non-zip file uploaded ..."

    graph_invariants_loc = os.path.join(data_dir, 'graphInvariants')
    makeDirIfNone([graph_invariants_loc])

    task_invariant_compute.dela(invariants, uploadedZip, graph_invariants_loc, 
        data_dir, in_graph_format, to_email)

    sendJobBeginEmail(to_email, invariants)

    return HttpResponse("Successful job submission, please " \
                          "await reception & completion emails at {0}".format(to_email))
  else:
    return HttpResponse("There was an error! If you believe it " \
                          "is on our end please email: {0}".format(settings.DEFAULT_FROM_EMAIL))
