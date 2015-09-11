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

# graph_upload.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.
from glob import glob
import os
from time import strftime, localtime

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from pipeline.forms import GraphUploadForm
from pipeline.utils.util import makeDirIfNone, writeBodyToDisk, saveFileToDisk
from pipeline.utils.util import sendJobBeginEmail
from pipeline.procs.inv_compute import invariant_compute
from pipeline.utils.zipper import unzip 
from pipeline.procs.run_invariants import run_invariants
from pipeline.tasks import task_invariant_compute
from pipeline.utils.util import get_script_prefix

def graphLoadInv(request, webargs=None):
  ''' Form '''
  if request.method == 'POST' and not webargs:
    form = GraphUploadForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():

      data = form.files['fileObj'] # get data
      invariants = form.cleaned_data['Select_Invariants_you_want_computed']

      data_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
      invariants_path = os.path.join(data_dir, 'graphInvariants')

      makeDirIfNone([data_dir])

      # We got a zip
      if os.path.splitext(data.name)[1] == '.zip':
        writeBodyToDisk(data.read(), data_dir)
        graphs = glob(os.path.join(data_dir,'*')) 

      else: # View only accepts a subset of file formats as regulated by template Validate func
        graphs = [os.path.join(data_dir, data.name)]
        saveFileToDisk(data, graphs[0])

      request.session['graph_format'] = form.cleaned_data['graph_format']
      request.session['email'] = form.cleaned_data['email']

      # Launch thread for graphs & email user
      sendJobBeginEmail(request.session['email'], invariants, genGraph=False)

      for graph_fn in graphs:
        task_invariant_compute.delay(invariants, graph_fn, invariants_path, 
                data_dir, form.cleaned_data['graph_format'], request.session['email'])

      request.session['success_msg'] = \
"""
Your job successfully launched. You should receive an email when your job begins and another one when it completes.<br/>
The process may take several hours (dependent on graph size) if you selected to compute all invariants.<br/>
If you do not see an email in your <i>Inbox</i> check the <i>Spam</i> folder and add <code>jhmrocp@cs.jhu.edu</code> 
to your safe list.
"""
      return HttpResponseRedirect(get_script_prefix()+'success')
  # Programmatic RESTful API
  elif request.method == 'POST' and webargs:
    pass
    """
    data_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
    makeDirIfNone([data_dir])

    uploadedZip = writeBodyToDisk(request.body, data_dir)[0] # Not necessarily a zip

    try: # Assume its a zip first
      unzip(uploadedZip, data_dir) # Unzip the zip
      os.remove(uploadedZip) # Delete the zip
    except:
      print "Non-zip file uploaded ..."
    graphs = glob(os.path.join(data_dir,'*'))

    try:
      request.session['invariants'] = webargs.split('/')[0].split(',')
      inGraphFormat = webargs.split('/')[1]
    except:
      return HttpResponse("Malformated input invariants list or graph format")

    request.session['graphInvariants'] = os.path.join(data_dir, 'graphInvariants')

    #############################################################################
    # TODO: This is where the work is done
    #############################################################################
    for graph_fn in graphs:
      invariant_fns = run_invariants(request.session['invariants'], graph_fn,
                        request.session['graphInvariants'], inGraphFormat)
      print 'Computing Invariants for annoymous project %s complete...' % graph_fn

      err_msg = ""
      out_fn = ""
      if len(webargs.split('/')) > 2:
        out_fn, err_msg = convert_graph(invariant_fns["out_graph_fn"], "graphml",
                request.session['graphInvariants'], *webargs.split('/')[2].split(','))

      #dwnldLoc = request.META['wsgi.url_scheme'] + '://' + \
       #             request.META['HTTP_HOST'] + data_dir.replace(' ','%20')

      dwnldLoc =  "http://mrbrain.cs.jhu.edu" + data_dir.replace(' ','%20')
      if err_msg:
        err_msg = "Completed with errors. View Data at: %s\n. Here are the errors:%s" % (dwnldLoc, err_msg)
        return HttpResponse(err_msg)

    return HttpResponse("View Data at: " + dwnldLoc)
    #############################################################################
    # END TODO: This is where the work is done
    #############################################################################
  # Browser
  """
  else:
    form = GraphUploadForm() # An empty, unbound form

  # Render the form
  return render_to_response(
      'graphupload.html',
      {'graphUploadForm': form},
      context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
  )
