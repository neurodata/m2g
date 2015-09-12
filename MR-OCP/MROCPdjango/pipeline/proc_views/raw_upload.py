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

# raw_upload.py
# Created by Disa Mhembere on 2015-05-28.
# Email: disa@jhu.edu

import argparse
import os
from time import strftime, localtime
import threading

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf import settings

from pipeline.forms import RawUploadForm
from pipeline.models import RawUploadModel
from pipeline.utils.util import saveFileToDisk, sendEmail
from pipeline.tasks import task_runc4

from pipeline.utils.util import get_script_prefix

def raw_upload(request):

  if request.method == "POST":
    form = RawUploadForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():
      # TODO: Alter save path
      data_dir = os.path.join(settings.MEDIA_ROOT, "c4", 
                strftime("%a%d%b%Y_%H.%M.%S/", localtime()), "derivatives")

      dti = form.cleaned_data["dti"]
      mprage = form.cleaned_data["mprage"]
      bvalue = form.cleaned_data["bvalue"]
      bvector = form.cleaned_data["bvector"]

      # Save all derivatives
      for _file in dti, mprage, bvalue, bvector:
        saveFileToDisk(_file, os.path.join(data_dir, _file.name))

      ru_model = RawUploadModel()
      ru_model.dtipath = os.path.join(data_dir, dti.name)
      ru_model.mpragepath = os.path.join(data_dir, mprage.name)
      ru_model.atlas = form.cleaned_data["atlas"]
      ru_model.graphsize = "big" if form.cleaned_data["graphsize"] == True else "small"
      ru_model.email = form.cleaned_data["email"] 
      ru_model.save() # Sync to Db

      task_runc4.delay(ru_model.dtipath, ru_model.mpragepath,
          os.path.join(data_dir, bvalue.name), os.path.join(data_dir, bvector.name), 
          form.cleaned_data["graphsize"], ru_model.atlas, form.cleaned_data["email"])

      sendEmail(form.cleaned_data["email"], "MR Images to graphs job started", 
              "Hello,\n\nYour job launched successfully. You will receive another email upon completion.\n\n")

      request.session["success_msg"] =\
"""
Your job successfully launched. You should receive an email to confirm launch
and another when it upon job completion. <br/> The process can take <i>several hours</i> in some cases.
"""
      return HttpResponseRedirect(get_script_prefix()+"success")

  else:
    form = RawUploadForm() # An empty, unbound form

  return render_to_response(
    "c4.html",
    {"RawUploadForm": form},
    context_instance=RequestContext(request)
    )
