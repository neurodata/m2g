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
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import get_script_prefix
from ocpipeline.forms import RawUploadForm
from ocpipeline.models import RawUploadModel
from ocpipeline.utils.util import makeDirIfNone, writeBodyToDisk, saveFileToDisk
from time import strftime, localtime

def raw_upload(request):

  if request.method == "POST":
    form = RawUploadForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():
      import pdb; pdb.set_trace()
      """
      nifti_paths = form.cleaned_data["niftis"]
      graph_size = form.cleaned_data["graphsize"]

      ru_model = RawUploadModel()
      ru_model.mpragepath = if len(nifti_paths) > 0: nifti_paths[0] else ""
      ru_model.dtipath = if len(nifti_paths) > 2: nifti_paths[2] else ""
      ru_model.fmripath = if len(nifti_paths) > 2: nifti_path[2] else ""
      ru_model.atlas = form.cleaned_data["atlas"]
      ru_model.graphsize = "big" if form.cleaned_data["graph_size"] == True else "small"
      email = form.cleaned_data["email"] 
      """
      return HttpResponseRedirect(get_script_prefix()+"success")

  else:
    form = RawUploadForm() # An empty, unbound form

  return render_to_response(
    "c4.html",
    {"RawUploadForm": form},
    context_instance=RequestContext(request)
    )

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()

if __name__ == "__main__":
  main()
