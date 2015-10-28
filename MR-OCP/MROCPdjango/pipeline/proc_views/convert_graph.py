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

# convert_graphs.py
# Created by Disa Mhembere on 2015-03-16.
# Email: disa@jhu.edu

import argparse
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

def getworkdirs():
  base_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('formUpload%a%d%b%Y_%H.%M.%S/', localtime()))
  save_dir = os.path.join(base_dir,'upload') # Save location of original uploads
  convert_file_save_loc = os.path.join(base_dir,'converted') # Save location of converted data
  if not os.path.exists(save_dir): os.makedirs(save_dir)
  if not os.path.exists(convert_file_save_loc): os.makedirs(convert_file_save_loc)
  return save_dir, convert_file_save_loc

def convert_graph(request):
  if (request.method == 'POST'):
    form = ConvertForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():
      upload_fn = form.files['fileObj'].name
      save_dir, convert_file_save_loc = getworkdirs()
      saved_file = os.path.join(save_dir, upload_fn)
      saveFileToDisk(form.files['fileObj'], saved_file)

      # If zip is uploaded
      if os.path.splitext(upload_fn)[1].strip() == '.zip':
        unzip(saved_file, save_dir)
        # Delete zip so its not included in the graphs we uploaded
        os.remove(saved_file)
        uploaded_files = glob(os.path.join(save_dir, "*")) # get the uploaded file names
      else:
        uploaded_files = [saved_file]

      #Browser """
      task_convert.delay(settings.MEDIA_ROOT, uploaded_files, convert_file_save_loc,
      form.cleaned_data['input_format'], form.cleaned_data['output_format'],
      form.cleaned_data["Email"])
      request.session['success_msg'] = \
"""
Your job successfully launched. You should receive an email when your job begins and another one when it completes.<br/>
The process may take several hours (dependent on graph size). If your job fails you will receive an email notification as well.<br/>
If you do not see an email in your <i>Inbox</i> check the <i>Spam</i> folder and add <code>jhmrocp@cs.jhu.edu</code> to your safe list.
"""
    return HttpResponseRedirect(get_script_prefix()+'success')
  else:
    form = ConvertForm() # An empty, unbound form

  # Render the form
  return render_to_response(
      'convertupload.html',
      {'convertForm': form},
      context_instance=RequestContext(request))
