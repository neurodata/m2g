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

"""
@author : Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: Module to hold the views of a Django one-click m2g pipeline
"""
import os, sys, re
from glob import glob
from random import randint
import subprocess
from time import strftime, localtime
os.environ["MPLCONFIGDIR"] = "/tmp/"

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import redirect
## Auth imports ##
from django.contrib.auth.decorators import login_required
# Registration
from django.contrib.auth import authenticate, login, logout


# Model & Form imports
from models import OwnedProjects

from mrcap import gengraph as gengraph
from  utils.filesorter import checkFileExtGengraph
from utils.create_dir_struct import create_dir_struct
from pipeline.utils.util import get_script_prefix

# Helpers
from utils.util import *

def testcelery(request):
  from pipeline.tasks import mrocp
  mrocp.delay("I'm serializable")
  return render_to_response("success.html", {"msg": "This is a success"})

def welcome(request):
  """ Little welcome message """
  return render_to_response("welcome.html", {"user":request.user},
                            context_instance=RequestContext(request))

def success(request):
  """ Successful completion of task"""
  return render_to_response("success.html", {"msg": request.session["success_msg"]}
                            ,context_instance=RequestContext(request))

def jobfailure(request):
  """ Job failure """
  return render_to_response("job_failure.html", {"msg": "Please check that your fiber streamline file and ROI's are correctly formatted"}
                            ,context_instance=RequestContext(request))

def getRootUrl(request):
  return request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST']

@login_required
def showdir(request):
  #directory = request.session['usrDefProjDir']
  return render('STUB')

def contact(request):
  return render_to_response('contact.html', context_instance=RequestContext(request))

def igraph_examples(request):
  return render_to_response("igraph_examples.html", context_instance=RequestContext(request))

def human_data_descrip(request):
  return render_to_response("human_data_descrip.html", context_instance=RequestContext(request))
