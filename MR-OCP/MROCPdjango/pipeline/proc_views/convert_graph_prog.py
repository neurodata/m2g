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

# convert_graphs_prog.py
# Created by Disa Mhembere on 2015-03-16.
# Email: disa@jhu.edu

import os
from glob import glob
from time import strftime, localtime

from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from pipeline.utils.util import get_script_prefix

from pipeline.forms import ConvertForm
from pipeline.utils.zipper import unzip
from computation.utils import convertTo
from pipeline.utils.util import writeBodyToDisk, saveFileToDisk
from pipeline.tasks import task_convert
from django.conf import settings
from pipeline.utils.util import get_download_path
from convert_graph import getworkdirs
from pipeline.utils.util import sendJobBeginEmail, check_email
from convert_graph import getworkdirs

# webargs is {email}{in_graph_format}/{out_graph_format}/[l]
def convert_graph_prog(request, webargs):
  if(request.method == 'POST' and webargs):
    split_webargs = webargs.split("/")
    link_only = False
    to_email = split_webargs[0]

    if (not check_email(to_email)):
      return HttpResponse("ERROR: Incorrect email address format")

    try:
      in_graph_format = split_webargs[1]
      if in_graph_format not in ("graphml", "ncol", "edgelist", "lgl", "pajek", "graphdb", "numpy", "mat"):
        return HttpResponse("ERROR: Unknown graph input format")

      out_graph_format = list(set(split_webargs[2].split(",")))
      if not out_graph_format: 
        return HttpResponse("ERROR: No output formats to compute provided")

      if len(split_webargs) == 4:
        if split_webargs[3] != "l":
          return HttpResponse("ERROR: Final parameter '{0}', expected 'l'".format(split_webargs[3]))
        else:
          link_only = True
    except:
      return HttpResponse("ERROR: Error with input graph format OR invariants chosen")


    save_dir, convert_file_save_loc = getworkdirs()
    uploaded_files = writeBodyToDisk(request.body, save_dir)# can only be one file # TODO: Check me

    # Check for zip
    if os.path.splitext(uploaded_files[0])[1].strip() == '.zip':
      zipper.unzip(uploaded_files[0], save_dir)
      # Delete zip so its not included in the graphs we uploaded
      os.remove(uploaded_files[0])
      uploaded_files = glob(os.path.join(save_dir, "*")) # get the uploaded file names

    task_convert.delay(settings.MEDIA_ROOT, uploaded_files, convert_file_save_loc,
    in_graph_format, out_graph_format, to_email)

    if link_only:
      return HttpResponse(get_download_path(convert_file_save_loc))

    return HttpResponse("Successful job submission, please " \
                          "await reception & completion emails at {0}".format(to_email))
  else:
    return HttpResponse("There was an error! If you believe it " \
                          "is on our end please email: {0}".format(settings.DEFAULT_FROM_EMAIL))
