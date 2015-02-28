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

@summary: Module to hold the views of a Django one-click MR-connectome pipeline
"""
import os, sys, re
from glob import glob
import threading
from random import randint
os.environ["MPLCONFIGDIR"] = "/tmp/"

import zipfile
import tempfile

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from django.core.files import File        # For programmatic file upload

# Model & Form imports
#from models import BuildGraphModel
from models import OwnedProjects
from models import GraphDownloadModel
from django_tables2 import RequestConfig
from graph_table import GraphTable

from forms import DownloadForm
from forms import GraphUploadForm
from forms import ConvertForm
from forms import PasswordResetForm
from forms import DownloadGraphsForm
from forms import DownloadQueryForm

## Data Processing imports ##
import paths
from mrcap import gengraph as gengraph
from mrcap.utils.downsample import downsample
from mrcap.utils import igraph_io

from  utils.filesorter import checkFileExtGengraph
import utils.zipper as zipper
from utils.create_dir_struct import create_dir_struct
from computation.utils.convertTo import convert_graph

from django.core.servers.basehttp import FileWrapper

import subprocess
from django.core.urlresolvers import get_script_prefix
from django.conf import settings

from time import strftime, localtime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import redirect

## Graph Analysis imports ##
import computation.composite.invariants as cci
import scipy.io as sio
from nibabel import load as nib_load

## Auth imports ##
from django.contrib.auth.decorators import login_required

# Registration
from django.contrib.auth import authenticate, login, logout

# Helpers
from utils.util import *

def default(request):
  """ Base url just redirects to welcome """
  return redirect(get_script_prefix()+"welcome", {"user":request.user})

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

def upload(request, webargs=None):
  """
  Programmatic interface for uploading data
  @param request: the request object

  @param webargs: POST data with userDefProjectName, site, subject, session,
        scanId, graphsize, [list of invariants to compute] info
  """
  if (webargs and request.method == 'POST'):
    # Check for malformatted input
    webargs = webargs[1:] if webargs.startswith('/') else webargs
    webargs = webargs[:-1] if webargs.endswith('/') else webargs

    if len(webargs.split('/')) == 7:
      [userDefProjectName, site, subject, session, scanId, graphsize, request.session['invariants']] = webargs.split('/')

      request.session['invariants'] = request.session['invariants'].split(',')
    elif len(webargs.split('/')) == 6:
      [userDefProjectName, site, subject, session, scanId, graphsize] = webargs.split('/')
    else:
      # Some sort of error
      return HttpResponseBadRequest ("Malformatted programmatic request. Check format of url and data requests")

    userDefProjectDir = adaptProjNameIfReq(os.path.join(settings.MEDIA_ROOT, 'public', userDefProjectName, site, subject, session, scanId))

    ''' Define data directory paths '''
    derivatives, graphs, request.session['graphInvariants'] = defDataDirs(userDefProjectDir)

    ''' Make appropriate dirs if they dont already exist '''
    create_dir_struct([derivatives, graphs,request.session["graphInvariants"]])
    print 'Directory structure created...'

    uploadFiles =  writeBodyToDisk(request.body, derivatives)

    # Check which file is which
    fiber_fn, data_atlas_fn = checkFileExtGengraph(uploadFiles) # Check & sort files
    if not data_atlas_fn:
      data_atlas_fn = settings.ATLASES.keys()[0]
    else:
      data_atlas_fn = os.path.join(derivatives, data_atlas_fn)

    ''' Data Processing '''
    if graphsize:
      request.session['Gfn']= call_gengraph(fiber_fn, data_atlas_fn, \
                              graphs, request.session['graphInvariants'],\
                              graphsize, run=True)

    else:
      return HttpResponseBadRequest ("Missing graph size. You must specify big or small")


    # Run invariants
    if request.session.has_key('invariants'):
      print "Computing invariants ..."

      invariant_fns = run_invariants(request.session['invariants'],\
                      request.session['Gfn'], request.session['graphInvariants'])

    #dwnldLoc = request.META['wsgi.url_scheme'] + '://' + \
                    #request.META['HTTP_HOST'] + userDefProjectDir.replace(' ','%20')
    dwnldLoc = "http://mrbrain.cs.jhu.edu" + userDefProjectDir.replace(' ','%20')

    return HttpResponse ( "Files available for download at " + dwnldLoc) # change to render of a page with a link to data result

  elif(not webargs):
    return HttpResponseBadRequest ("Expected web arguments to direct project correctly")

  else:
    return HttpResponseBadRequest ("Expected POST data, but none given")

####################################################
def download(request, webargs=None):

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

        dl_format = request.POST.get("dl_format")

        if not selected_files:
          return HttpResponseRedirect(get_script_prefix()+"download")

        # Something selected for dl/Convert+dl
        else:
          if (len(selected_files) > MAX_NUM_GRAPH_DLS and request.POST.has_key("human")):
            data_dir = os.path.join(settings.MEDIA_ROOT, "tmp",
                                   strftime("download_%a%d%b%Y_%H.%M.%S/", localtime()))
            dwnld_loc = "http://mrbrain.cs.jhu.edu" + data_dir.replace(" ","%20")
            #dwnld_loc = request.META['wsgi.url_scheme'] + "://" + request.META["HTTP_HOST"] + data_dir.replace(" ","%20")

            sendEmail(request.POST.get("email"), "Job launch notification",
                      "Your download request was received. You will receive an email when it completes.\n\n")

            # Testing only
            #scale_convert(selected_files, dl_format, ds_factor, ATLASES,
            #              request.POST.get("email"), dwnld_loc, os.path.join(data_dir, "archive.zip")) # Testing only
            thr = threading.Thread(target=scale_convert, args=(selected_files, dl_format, ds_factor, ATLASES,
                                      request.POST.get("email"), dwnld_loc, os.path.join(data_dir, "archive.zip")))
            thr.start()

            request.session['success_msg'] = \
"""
Your job successfully launched. You should receive an email when your job begins and another one when it completes.<br/>
The process may take several hours (dependent on graph size). If your job fails you will receive an email notification as well.<br/>
If you do not see an email in your <i>Inbox</i> check the <i>Spam</i> folder and add <code>jhmrocp@cs.jhu.edu</code> to your safe list.
"""
            return HttpResponseRedirect(get_script_prefix()+'success')
          else:
            print "Beginning interactive download ..."
            temp = scale_convert(selected_files, dl_format, ds_factor, ATLASES)
            if isinstance(temp, str):
              return render_to_response("job_failure.html",
                  {"msg":temp}, context_instance=RequestContext(request))

            # TODO: Possibly use django.http.StreamingHttpResponse for this
            wrapper = FileWrapper(temp)
            response = HttpResponse(wrapper, content_type='application/zip')
            response['Content-Disposition'] = ('attachment; filename=archive.zip')
            response['Content-Length'] = temp.tell()
            temp.seek(0)

            return response
      else:
        return HttpResponseRedirect(get_script_prefix()+"download")

  else:
    tbls = []
    for genus in settings.GENERA:
      table = GraphTable(GraphDownloadModel.objects.filter(genus=genus))
      table.set_html_name(genus.capitalize()) # Set the html __repr__
      # TODO: Alter per_page limit to +25
      RequestConfig(request, paginate={"per_page":25}).configure(table) # Let each table re-render given a request
      #table.columns["url"].header = "Download Link"

      dl_form = DownloadGraphsForm()
      dl_form.set_name(genus)

      tbls.append((table, dl_form))

  return render_to_response("downloadgraph.html", {"genera":tbls, "query":DownloadQueryForm()},
                            context_instance=RequestContext(request))

###################################################
#           Asynchronous methods                  #
###################################################

def asyncInvCompute(request):

  #dwnldLoc = request.META['wsgi.url_scheme'] + '://' +  request.META['HTTP_HOST']
  dwnldLoc = "http://mrbrain.cs.jhu.edu" + \
                    request.session['dataDir'].replace(' ','%20')

  for graph_fn in request.session['uploaded_graphs']:
    try:
      invariant_fns = run_invariants(request.session['invariants'], graph_fn,
                      request.session['graphInvariants'], graph_format=request.session['graph_format'])

      if isinstance(invariant_fns, str):
        raise Exception
      else:
        print 'Invariants for annoymous project %s complete...' % graph_fn

    except Exception, msg:
      msg = """
Hello,\n\nYour most recent job failed possibly because:\n- the graph '%s' you
uploaded does not match any accepted type.\n\n"You may have some partially
completed data here: %s.\nPlease check these and try again.\n\n
""" % (os.path.basename(graph_fn), dwnldLoc)

      sendJobFailureEmail(request.session['email'], msg)
      return

  # Email user of job finished
  sendJobCompleteEmail(request.session['email'], dwnldLoc)

######################################################

def scale_convert(selected_files, dl_format, ds_factor, ATLASES, email=None, dwnld_loc=None, zip_fn=None):
  # Debug
  print "Entering scale function ..."
  try:
    if dl_format == "graphml" and ds_factor == 0:
      temp = zipper.zipfiles(selected_files, use_genus=True, zip_out_fn=zip_fn)

    else:
      files_to_zip = {}

      for fn in selected_files:
        # No matter what we need a temp file
        print "Creating temp file ..."
        tmpfile = tempfile.NamedTemporaryFile("w", delete=False, dir="/data/pytmp")
        print "Temp file %s created ..." % tmpfile.name
        tmpfile.close()

        # Downsample only valid for *BIG* human brains!
        # *NOTE: If smallgraphs are ingested this will break

        if ds_factor and get_genus(fn) == "human":
          if isinstance(ds_factor, int):
            print "downsampling to factor %d" % ds_factor
            g = downsample(igraph_io.read_arbitrary(fn, "graphml"), ds_factor)
            print "downsample complete"
          else:
            g = downsample(igraph_io.read_arbitrary(fn, "graphml"), atlas=nib_load(ATLASES[ds_factor]))
        else:
          g = igraph_io.read_arbitrary(fn, "graphml")

        # Write to `some` format
        if dl_format == "mm":
          igraph_io.write_mm(g, tmpfile.name)
        else:
          g.write(tmpfile.name, format=dl_format)

        files_to_zip[fn] = tmpfile.name

      temp = zipper.zipfiles(files_to_zip, use_genus=True, zip_out_fn=zip_fn, gformat=dl_format)
      # Del temp files
      for tmpfn in files_to_zip.values():
        print "Deleting %s ..." % tmpfn
        os.remove(tmpfn)

  except Exception, msg:
    print "An exception was thrown and caught with message %s!" % msg
    if email:
      msg = """
Hello,\n\nYour most recent job failed to complete.
\n"You may have some partially completed data here: %s.\n\n
""" % dwnld_loc

      sendJobFailureEmail(email, msg)
      return
    else:
      return 'An error occurred while processing your request. Please send an email to \
              <a href="mailto:jhmrocp@cs.jhu.edu">jhmrocp@cs.jhu.edu</a> with the details of your request.'

  if email:
    # Email user of job finished
    sendJobCompleteEmail(email, dwnld_loc)
    return

  return temp # Case where its an iteractive download

#########################################
#	*******************		#
#	  CONVERT GRAPH FORMAT		#
#########################################

def convert(request, webargs=None):
  """ Browser """
  if (request.method == 'POST' and not webargs):
    form = ConvertForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():

      baseDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('formUpload%a%d%b%Y_%H.%M.%S/', localtime()))
      saveDir = os.path.join(baseDir,'upload') # Save location of original uploads
      convertFileSaveLoc = os.path.join(baseDir,'converted') # Save location of converted data

      if not (os.path.exists(convertFileSaveLoc)):
        os.makedirs(convertFileSaveLoc)

      savedFile = os.path.join(saveDir, request.FILES['fileObj'].name)

      saveFileToDisk(request.FILES['fileObj'], savedFile)

      # If zip is uploaded
      if os.path.splitext(request.FILES['fileObj'].name)[1].strip() == '.zip':
        zipper.unzip(savedFile, saveDir)
        # Delete zip so its not included in the graphs we uploaded
        os.remove(savedFile)
        uploadedFiles = glob(os.path.join(saveDir, "*")) # get the uploaded file names

      else:
        uploadedFiles = [savedFile]

      err_msg = ""
      outfn = ""
      for fn in uploadedFiles:
        outfn, err_msg = convert_graph(fn, form.cleaned_data['input_format'],
                        convertFileSaveLoc, *form.cleaned_data['output_format'])

      #dwnldLoc = request.META['wsgi.url_scheme'] + '://' + \
      #              request.META['HTTP_HOST'] + convertFileSaveLoc.replace(' ','%20')

      dwnldLoc = "http://mrbrain.cs.jhu.edu" + convertFileSaveLoc.replace(' ','%20')

      if (err_msg):
        err_msg = "Your job completed with errors. The result can be found <a href=\"%s\" target=\"blank\">here</a>.<br> Message %s" % (dwnldLoc, err_msg)
        return render_to_response(
        'convertupload.html',
        {'convertForm': form, 'err_msg': err_msg+"\n"},
        context_instance=RequestContext(request))
      #else
      return HttpResponseRedirect(dwnldLoc)

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

#########################################
#	*******************		#
#	   PROCESS DATA			#
#########################################

def call_gengraph(fiber_fn, data_atlas_fn, graphs, graphInvariants, graphsize, run = False):
  '''
  Run graph building and other related scripts
  @param fiber_fn: fiber tract file
  @param data_atlas_fn: the data atlas defining ROIs and region

  @param graphs: Dir where biggraphs & smallgraphs are saved
  @param graphInvariants:  Dir where graph invariants are saved
  @param graphsize: the size of the graph 'big' or 'small'
  @param run: Whether or not to run processor intensive jobs. Default is - false so nothing is actually run
  '''

  baseName = getFiberID(fiber_fn) #VERY TEMPORARY

  Gfn = os.path.join(graphs, baseName) # partial name

  if (run):
    if graphsize.lower().startswith("s"):
      print("Running Small gengraph ...")
      Gfn+="smgr.graphml"

      # Note: Some included atlases are present
      gengraph.genGraph(fiber_fn, data_atlas_fn, Gfn, bigGraph=False, **settings.ATLASES)

    elif graphsize.lower().startswith("b"):
      print("\nRunning Big gengraph ...")
      Gfn+="bggr.graphml"
      gengraph.genGraph(fiber_fn, data_atlas_fn, Gfn, bigGraph=True, **settings.ATLASES)
    else:
      print '[ERROR]: Graphsize Unkwown' # should never happen
  return Gfn

