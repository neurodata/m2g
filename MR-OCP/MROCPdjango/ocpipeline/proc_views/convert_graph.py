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
import threading

from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import get_script_prefix

from ocpipeline.forms import ConvertForm
from ocpipeline.utils.zipper import unzip
from computation.utils.convertTo import convert_graph
from ocpipeline.utils.util import writeBodyToDisk
from ocpipeline.procs.convert import convert


def convert_graph(request, webargs=None):

  if (request.method == 'POST' and not webargs):
   form = ConvertForm(request.POST, request.FILES) # instantiating form
   if form.is_valid():
    """ Browser """
    """
    convert(settings.MEDIA_ROOT, form.files['fileObj'].name, form.files['fileObj'],
        form.cleaned_data['input_format'], form.cleaned_data['output_format'], 
        form.cleaned_data["Email"])
    """

    thr = threading.Thread(target=convert, args=(settings.MEDIA_ROOT, 
      form.files['fileObj'].name, form.files['fileObj'], form.cleaned_data['input_format'], 
      form.cleaned_data['output_format'], form.cleaned_data["Email"]))
    thr.start()

    request.session['success_msg'] = \
"""
Your job successfully launched. You should receive an email when your job begins and another one when it completes.<br/>
The process may take several hours (dependent on graph size). If your job fails you will receive an email notification as well.<br/>
If you do not see an email in your <i>Inbox</i> check the <i>Spam</i> folder and add <code>jhmrocp@cs.jhu.edu</code> to your safe list.
"""
    return HttpResponseRedirect(get_script_prefix()+'success')

  elif(request.method == 'POST' and webargs):
    # webargs is {inFormat}/{outFormat}
    inFormat = webargs.split('/')[0] # E.g 'graphml'| 'dot' | 'leda'
    outFormat =  webargs.split('/')[1].split(',')

    outFormat = list(set(outFormat)) # Eliminate duplicates if any exist

    baseDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('progUpload%a%d%b%Y_%H.%M.%S/', localtime()))
    saveDir = os.path.join(baseDir,'upload') # Save location of original uploads
    convertFileSaveLoc = os.path.join(baseDir,'converted') # Save location of converted data

    if not os.path.exists(saveDir): os.makedirs(saveDir)
    if not os.path.exists(convertFileSaveLoc): os.makedirs(convertFileSaveLoc)

    uploadedFiles = writeBodyToDisk(request.body, saveDir)# can only be one file # TODO: Check me

    # Check for zip
    if os.path.splitext(uploadedFiles[0])[1].strip() == '.zip':
        zipper.unzip(uploadedFiles[0], saveDir)
        # Delete zip so its not included in the graphs we uploaded
        os.remove(uploadedFiles[0])
        uploadedFiles = glob(os.path.join(saveDir, "*")) # get the uploaded file names

    err_msg = ""
    outfn = ""
    for fn in uploadedFiles:
      outfn, err_msg = convert_graph(fn, inFormat,
                        convertFileSaveLoc, *outFormat)

    dwnldLoc = "http://mrbrain.cs.jhu.edu" + convertFileSaveLoc.replace(' ','%20')

    if err_msg:
      err_msg = "Completed with errors. View Data at: %s\n. Here are the errors:%s" % (dwnldLoc, err_msg)
      return HttpResponse(err_msg)

    elif len(webargs.split("/")) > 2:
      if (outfn and len(outFormat) == 1):
        return HttpResponse(dwnldLoc + "/" + outfn.split("/")[-1])
      else:
        return HttpResponse(dwnldLoc)

    return HttpResponse ("Converted files available for download at " + dwnldLoc + " . The directory " +
            "may be empty if you try to convert from, and to the same format.") # change to render of a page with a link to data result

  else:
    form = ConvertForm() # An empty, unbound form

  # Render the form
  return render_to_response(
      'convertupload.html',
      {'convertForm': form},
      context_instance=RequestContext(request))


def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()


if __name__ == "__main__":
  main()
