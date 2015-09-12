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

# download.py
# Created by Disa Mhembere on 2015-03-15.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import os
import threading
from time import strftime, localtime

from django.http import HttpResponseRedirect, HttpResponse
from pipeline.utils.util import get_script_prefix

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django_tables2 import RequestConfig

from pipeline.graph_table import GraphTable
from pipeline.models import GraphDownloadModel
from pipeline.forms import DownloadGraphsForm
from pipeline.forms import DownloadQueryForm
from pipeline.utils.util import sendEmail
from pipeline.tasks import task_scale
from pipeline.utils.util import get_download_path

def download(request):
  MAX_NUM_GRAPH_DLS = 1
  ATLASES = {"desikan": os.path.join(settings.ATLAS_DIR, "desikan_atlas.nii") ,
              "slab": os.path.join(settings.ATLAS_DIR, "slab_atlas.nii")}

  if request.method == "POST":
    if request.POST.keys()[0] == "query_type": # Means we are doing a search
      form = DownloadQueryForm(request.POST)
      if form.is_valid():
        gdmof = GraphDownloadModel.objects.filter # typedef
        st = str(".*"+ ".*".join(form.cleaned_data["query"].strip().split()) +".*") # Search Term

        if form.cleaned_data["query_type"] == "all":
          table = GraphTable(
              gdmof(genus__iregex=st)      | gdmof(filepath__iregex=st) |
              gdmof(region__iregex=st)     | gdmof(numvertex__iregex=st)|
              gdmof(numedge__iregex=st)    | gdmof(graphattr__iregex=st)|
              gdmof(vertexattr__iregex=st) |  gdmof(edgeattr__iregex=st)|
              gdmof(sensor__iregex=st)     | gdmof(source__iregex=st)   |
              gdmof(project__iregex=st)
           )
        elif form.cleaned_data["query_type"] == "attribute":
          table = GraphTable(
              gdmof(graphattr__iregex=st)| gdmof(vertexattr__iregex=st)|
              gdmof(edgeattr__iregex=st)
           )
        elif form.cleaned_data["query_type"] == "name":
          table = GraphTable( gdmof(filepath__iregex=st) )
        elif form.cleaned_data["query_type"] == "genus":
          table = GraphTable( gdmof(genus__iregex=st) )
        elif form.cleaned_data["query_type"] == "region":
          table = GraphTable( gdmof(region__iregex=st) )
        elif form.cleaned_data["query_type"] == "project":
          table = GraphTable( gdmof(project__iregex=st) )

        # NOTE: Or equal to as well
        elif form.cleaned_data["query_type"] == "numvertex_gt":
          table = GraphTable( gdmof(numvertex__gte=int(form.cleaned_data["query"])) )
        elif form.cleaned_data["query_type"] == "numedge_gt":
          table = GraphTable( gdmof(numedge__gte=int(form.cleaned_data["query"])) )

        elif form.cleaned_data["query_type"] == "numvertex_lt":
          table = GraphTable( gdmof(numvertex__lte=int(form.cleaned_data["query"])) )
        elif form.cleaned_data["query_type"] == "numedge_lt":
          table = GraphTable( gdmof(numedge__lte=int(form.cleaned_data["query"])) )

        elif form.cleaned_data["query_type"] == "sensor":
          table = GraphTable( gdmof(sensor__iregex=st) )
        elif form.cleaned_data["query_type"] == "source":
          table = GraphTable( gdmof(source__iregex=st) )

        if (len(table.rows) == 0):
          table = None # Get the no results message to show up
        else:
          table.set_html_name("Search Results")

        return render_to_response("downloadgraph.html", {"genera":[],
          "query_result":table}, context_instance=RequestContext(request))
      else:
        return HttpResponseRedirect(get_script_prefix()+"download")

    else: # We just want to download specific files

      form = DownloadGraphsForm(request.POST)

      if form.is_valid():
        selected_files = request.POST.getlist("selection")
        ds_factor = 0 if not request.POST.get("ds_factor") else request.POST.get("ds_factor")

        if ds_factor not in ATLASES.keys():
          ds_factor = int(ds_factor)

        dl_format = form.cleaned_data["dl_format"]

        if not selected_files:
          return HttpResponseRedirect(get_script_prefix()+"download")

        # Something selected for dl/Convert+dl
        else:
          data_dir = os.path.join(settings.MEDIA_ROOT, "tmp",
                                 strftime("download_%a%d%b%Y_%H.%M.%S/", localtime()))
          dwnld_loc = get_download_path(data_dir)

          sendEmail(form.cleaned_data["Email"], "Job launch notification",
                  "Your download request was received. You will receive an email when it completes.\n\n")

          # Testing only
          task_scale.delay(selected_files, dl_format, ds_factor, ATLASES, form.cleaned_data["Email"], 
          dwnld_loc, os.path.join(data_dir, "archive.zip")) # Testing only

          request.session['success_msg'] = \
"""
Your job successfully launched. You should receive an email when your job begins and another 
one when it completes.<br/> The process may take several hours (dependent on graph size). 
If your job fails you will receive an email notification as well.<br/>
If you do not see an email in your <i>Inbox</i> check the <i>Spam</i> folder and add 
<code>jhmrocp@cs.jhu.edu</code> to your safe list.
"""
          return HttpResponseRedirect(get_script_prefix()+'success')
      else:
        return HttpResponseRedirect(get_script_prefix()+"download")

  else:
    tbls = []
    for genus in settings.GENERA:
      table = GraphTable(GraphDownloadModel.objects.filter(genus=genus))
      table.set_html_name(genus.capitalize()) # Set the html __repr__
      # TODO: Alter per_page limit to +25
      RequestConfig(request, paginate={"per_page":25}).configure(table) # Each table re-render given a request
      #table.columns["url"].header = "Download Link"

      dl_form = DownloadGraphsForm()
      dl_form.set_name(genus)

      tbls.append((table, dl_form))

  return render_to_response("downloadgraph.html", {"genera":tbls, "query":DownloadQueryForm()},
                            context_instance=RequestContext(request))
