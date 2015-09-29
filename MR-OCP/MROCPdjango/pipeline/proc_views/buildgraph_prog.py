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

# buildgraph_prog.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import os
from time import strftime, localtime

from django.conf import settings
from django.http import HttpResponse

from pipeline.utils.util import get_script_prefix
from pipeline.utils.util import adaptProjNameIfReq, defDataDirs
from pipeline.utils.util import sendJobBeginEmail
from pipeline.models import BuildGraphModel
from pipeline.tasks import task_build
from pipeline.utils.util import writeBodyToDisk

def getworkdir():
  base_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('buildUpload%a%d%b%Y_%H.%M.%S/', localtime()))
  save_dir = os.path.join(base_dir, 'buildupload') # Save location of original uploads
  if not os.path.exists(save_dir): os.makedirs(save_dir)
  return save_dir

def build_graph_prog(request, webargs):
  if request.method == "POST" and webargs:
    
    webargs = webargs.split("/")
    proj_dir, site, subject, session, scanId = webargs[:5]
    email = webargs[6]
    invariants = webargs[7:]

    proj_dir = os.path.join("public", proj_dir)

    # Adapt project name if necesary on disk
    proj_dir = adaptProjNameIfReq(os.path.join(
        settings.MEDIA_ROOT, proj_dir)) # Fully qualify AND handle identical projects

    usrDefProjDir = os.path.join(proj_dir, site, subject, session, scanId)
    """ Define data directory paths """
    derivatives, graphs = defDataDirs(usrDefProjDir)

    # Create a model object to save data to DB
    grModObj = BuildGraphModel(project_name = webargs[0])
    grModObj.location = usrDefProjDir # The particular scan location

    grModObj.site = site
    grModObj.subject = subject
    grModObj.session = session
    grModObj.scanId = scanId
    grModObj.save() # Save project data to DB after file upload

    graph_size = webargs[5]
    save_dir = getworkdir()
    uploaded_files = writeBodyToDisk(request.body, save_dir)
    graph_loc = os.path.join(save_dir, "graphs")
    if not os.path.exists(graph_loc): os.makedirs(graph_loc)

    # add entry to owned project
    if request.user.is_authenticated():
      ownedProjModObj = OwnedProjects(project_name=grModObj.project_name, \
        owner=grModObj.owner, is_private=form.cleaned_data["Project_Type"] == "private")
      ownedProjModObj.save()

    print "\nSaving all files complete..."

    # TEST #
    """
    derivatives = "/home/disa/test/build_test"
    graphs = derivatives
    # END TEST #
    """

    sendJobBeginEmail(email, invariants)
    task_build.delay(save_dir, graph_loc, graph_size, invariants, save_dir, email)
    return HttpResponse("Successful job submission, please " \
                          "await reception & completion emails at {0}".format(email))
  else:
    return HttpResponse("There was an error! If you believe it " \
                          "is on our end please email: {0}".format(settings.DEFAULT_FROM_EMAIL))
