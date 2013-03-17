#!/usr/bin/python

'''
@author : Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: Module to hold the views of a Django one-click MR-connectome pipeline
'''

import os, sys, re
os.environ['MPLCONFIGDIR'] = '/tmp/'
#import matplotlib
#matplotlib.use( 'Agg' )

import zipfile
import tempfile

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from django.core.files import File        # For programmatic file upload

# Model imports
from models import ConvertModel
from models import BuildGraphModel
from forms import DownloadForm
from forms import GraphUploadForm
from forms import ConvertForm
from forms import BuildGraphForm
from forms import PasswordResetForm

import mrpaths

''' Data Processing imports'''
from mrcap import gengraph as gengraph

import filesorter as filesorter
import zipper as zipper
import createDirStruct as createDirStruct
import computation.convertTo as convertTo

from django.core.servers.basehttp import FileWrapper

import subprocess
from django.core.urlresolvers import get_script_prefix
from django.conf import settings

from time import strftime, localtime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import redirect

####################
## Graph Analysis ##
####################

from computation.scanstat_degr import calcScanStat_Degree
from computation.clustCoeff import calcLocalClustCoeff
from computation.loadAdjMatrix import loadAdjMat
from computation.triCount_MAD import eignTriLocal_MAD
from computation.degree import calcDegree
from computation.MAD import calcMAD
from computation.eigen import calcEigs
from computation.clustCoeff import calcLocalClustCoeff
from computation.triCount_deg_MAD import eignTriLocal_deg_MAD

from django.contrib.auth import authenticate, login, logout

import scipy.io as sio

# Helpers
from util import *

''' Base url just redirects to welcome '''
def default(request):
  return redirect(get_script_prefix()+'welcome', {"user":request.user})

''' Little welcome message '''
def welcome(request):
  #import pdb; pdb.set_trace()
  return render_to_response('welcome.html', {"user":request.user},
                            context_instance=RequestContext(request))


# Login decorator
#from django.contrib.auth.decorators import login_required
#@login_required(redirect_field_name='my_redirect_field')
#@login_required # OR EASIER
def buildGraph(request):
  #request.session.clear()

  if request.method == 'POST':
    form = BuildGraphForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():
      print "Uploading files..."

      # Acquire proj names
      userDefProjectName = form.cleaned_data['UserDefprojectName']
      site = form.cleaned_data['site']
      subject = form.cleaned_data['subject']
      session = form.cleaned_data['session']
      scanId = form.cleaned_data['scanId']

      userDefProjectName = adaptProjNameIfReq(os.path.join(settings.MEDIA_ROOT, userDefProjectName)) # Fully qualify AND handle identical projects

      request.session['usrDefProjDir'] = os.path.join(userDefProjectName, site, subject, session, scanId)
      request.session['scanId'] = scanId

      ''' Define data directory paths '''
      request.session['derivatives'], request.session['rawdata'], request.session['graphs'],\
          request.session['graphInvariants'],request.session['images']= defDataDirs(request.session['usrDefProjDir'])

      grModObj = BuildGraphModel(derivfile = request.FILES['fiber_file'])
      grModObj._meta.get_field('derivfile').upload_to = request.session['derivatives'] # route files to correct location

      grModObj2 = BuildGraphModel(derivfile = request.FILES['roi_raw_file'])
      grModObj2._meta.get_field('derivfile').upload_to = request.session['derivatives']

      grModObj3 = BuildGraphModel(derivfile =  request.FILES['roi_xml_file'])
      grModObj3._meta.get_field('derivfile').upload_to = request.session['derivatives']

      grModObj.projectName = grModObj2.projectName = grModObj3.projectName =  form.cleaned_data['UserDefprojectName']# set project name
      grModObj.site = grModObj2.site = grModObj3.site =  form.cleaned_data['site']# set the site
      grModObj.subject = grModObj2.subject = grModObj3.subject =  form.cleaned_data['subject']# set the subject
      grModObj.session = grModObj2.session = grModObj3.session =  form.cleaned_data['session']# set the session
      grModObj.scanId = grModObj2.scanId = grModObj3.scanId =  form.cleaned_data['scanId']# set the scanId

      request.session['invariants'] = form.cleaned_data['Select_Invariants_you_want_computed']

      request.session['graphsize'] = form.cleaned_data['Select_graph_size']

      ''' Acquire fileNames '''
      fiber_fn = form.cleaned_data['fiber_file'].name # get the name of the file input by user
      roi_raw_fn = form.cleaned_data['roi_raw_file'].name
      roi_xml_fn = form.cleaned_data['roi_xml_file'].name

      ''' Save files to temp location '''
      grModObj.save()
      grModObj2.save()
      grModObj3.save()

      print '\nSaving all files complete...'

      ''' Make appropriate dirs if they dont already exist '''
      createDirStruct.createDirStruct([request.session['derivatives'], request.session['rawdata'],\
          request.session['graphs'], request.session['graphInvariants'], request.session['images']])

      # Redirect to Processing page
      return HttpResponseRedirect(get_script_prefix()+'processinput')
  else:
    form = BuildGraphForm() # An empty, unbound form

  # Render the form
  return render_to_response(
      'buildgraph.html',
      {'buildGraphform': form},
      context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
  )

''' Successful completion of task'''
def success(request):
  return render_to_response('success.html')

def processInputData(request):
  '''
  Extract File name & determine what file corresponds to what for gengraph
  @param request: the request object
  '''
  filesInUploadDir = os.listdir(request.session['derivatives'])

  roi_xml_fn, fiber_fn, roi_raw_fn = filesorter.checkFileExtGengraph(filesInUploadDir) # Check & sort files

  for fileName in [roi_xml_fn, fiber_fn, roi_raw_fn]:
    if fileName == "": # Means a file is missing from i/p
      return render_to_response('pipelineUpload.html', context_instance=RequestContext(request)) # Missing file for processing Gengraph

  baseName = fiber_fn[:-9] #MAY HAVE TO CHANGE

  ''' Fully qualify file names '''
  fiber_fn = os.path.join(request.session['derivatives'], fiber_fn)
  roi_raw_fn = os.path.join(request.session['derivatives'], roi_raw_fn)
  roi_xml_fn = os.path.join(request.session['derivatives'], roi_xml_fn)

  request.session['smGrfn'], request.session['bgGrfn'], request.session['lccfn'],request.session['SVDfn'] \
      = processData(fiber_fn, roi_xml_fn, roi_raw_fn,request.session['graphs'], request.session['graphInvariants'], request.session['graphsize'], True)

  # Run ivariants here
  if len(request.session['invariants']) > 0:
    print "Computing invariants"
    if (request.session['graphsize'] == 'big'):
      lccG = loadAdjMat(request.session['bgGrfn'], request.session['lccfn'])

    elif (request.session['graphsize'] == 'small'):
      lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']

    request.session['invariant_fns'] =  runInvariants(lccG, request.session)
  return HttpResponseRedirect(get_script_prefix()+'confirmdownload', context_instance=RequestContext(request))

def confirmDownload(request):

  if request.method == 'POST':
    form = DownloadForm(request.POST) # instantiating form
    if form.is_valid():
      invConvertToFormats = form.cleaned_data['Select_Invariant_conversion_format'] # Which form to convert to
      grConvertToFormats = form.cleaned_data['Select_Graph_conversion_format']
      dataReturn = form.cleaned_data['Select_output_type']

      for fileFormat in invConvertToFormats:
        if fileFormat == '.mat':
          convertTo.convertLCCNpyToMat(request.session['lccfn'])
          convertTo.convertSVDNpyToMat(request.session['SVDfn'])

        # Conversion of all files
        for inv in request.session['invariant_fns'].keys():
          if isinstance(request.session['invariant_fns'][inv], list): # Case of eigs
            for fn in request.session['invariant_fns'][inv]:
              convertTo.convertAndSave(fn, fileFormat, getDirFromFilename(fn), inv)
          else: # case of all other invariants
            convertTo.convertAndSave(request.session['invariant_fns'][inv], fileFormat, \
                                getDirFromFilename(request.session['invariant_fns'][inv]) , inv)

      for fileFormat in grConvertToFormats:
        if request.session['graphsize'] == 'big':
          convertTo.convertGraph(request.session['bgGrfn'], fileFormat)
        elif request.session['graphsize'] == 'small':
          convertTo.convertGraph(request.session['smGrfn'], fileFormat)

      if dataReturn == 'vd': # View data directory
        dataUrlTail = request.session['usrDefProjDir']
        # request.session.clear() # Very important
        return HttpResponseRedirect('http://mrbrain.cs.jhu.edu' + dataUrlTail.replace(' ','%20'))

      elif dataReturn == 'dz': #Download all as zip
        return HttpResponseRedirect(get_script_prefix()+'zipoutput')

  else:
    form = DownloadForm()

  return render_to_response('confirmDownload.html',{'downloadForm': form},\
                  context_instance=RequestContext(request))

def zipProcessedData(request):
  '''
  Compress data products to single zip for upload
  @param request: the request object
  '''
  print '\nBeginning file compression...'
  # Take dir with multiple scans, compress it & send it off

  ''' Zip it '''
  #temp = zipper.zipFilesFromFolders(dirName = request.session['usrDefProjDir'])
  temp = zipper.zipper(request.session['usrDefProjDir'], zip_file = request.session['usrDefProjDir'] + '.zip')
  ''' Wrap it '''
  wrapper = FileWrapper(temp)
  response = HttpResponse(wrapper, content_type='application/zip')
  response['Content-Disposition'] = ('attachment; filename='+ request.session['scanId'] +'.zip')
  response['Content-Length'] = temp.tell()
  temp.seek(0)

  # request.session.clear() # Very Important
  ''' Send it '''
  return response

def upload(request, webargs=None):
  """
  Programmatic interface for uploading data
  @param request: the request object

  @param webargs: POST data with userDefProjectName, site, subject, session, scanId, graphsize, [list of invariants to compute] info
  """
  # request.session.clear()

  if (webargs and request.method == 'POST'):
    # Check for malformatted input
    webargs = webargs[1:] if webargs.startswith('/') else webargs
    webargs = webargs[:-1] if webargs.endswith('/') else webargs

    if len(webargs.split('/')) == 7:
      [userDefProjectName, site, subject, session, scanId, graphsize, request.session['invariants'] ] = webargs.split('/')
      request.session['invariants'] = request.session['invariants'].split(',')
    elif len(webargs.split('/')) == 6:
      [userDefProjectName, site, subject, session, scanId, graphsize] = webargs.split('/')

    userDefProjectDir = adaptProjNameIfReq(os.path.join(settings.MEDIA_ROOT, userDefProjectName, site, subject, session, scanId))

    ''' Define data directory paths '''
    derivatives, rawdata,  graphs, request.session['graphInvariants'], images = defDataDirs(userDefProjectDir)

    ''' Make appropriate dirs if they dont already exist '''
    createDirStruct.createDirStruct([derivatives, rawdata, graphs, request.session['graphInvariants'], images])
    print 'Directory structure created...'

    uploadFiles =  writeBodyToDisk(request.body, derivatives)

    # Check which file is which
    roi_xml_fn, fiber_fn, roi_raw_fn = filesorter.checkFileExtGengraph(uploadFiles) # Check & sort files

    ''' Data Processing '''
    if (re.match(re.compile('(b|big)', re.IGNORECASE), graphsize)):
      request.session['graphsize'] = 'big'
      request.session['smGrfn'], request.session['bgGrfn'], lccfn, SVDfn \
        = processData(fiber_fn, roi_xml_fn, roi_raw_fn,graphs, request.session['graphInvariants'], request.session['graphsize'],True) # Change to false to not process anything

      # process invariants if requested
      if request.session['invariants']:
        lccG = loadAdjMat(request.session['bgGrfn'], lccfn)

    elif(re.match(re.compile('(s|small)', re.IGNORECASE), graphsize)):
      request.session['graphsize'] = 'small'
      request.session['smGrfn'], request.session['bgGrfn'], lccfn, SVDfn \
        = processData(fiber_fn, roi_xml_fn, roi_raw_fn,graphs, request.session['graphInvariants'], request.session['graphsize'],True) # Change to false to not process anything

      if request.session['invariants']:
        lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']
    else:
      return django.http.HttpResponseBadRequest ("Missing graph size. Specify big or small")

    if request.session['invariants']:
      invariant_fns =  runInvariants(lccG, request.session)

    #ret = rzfile.printdir()
    #ret = rzfile.testzip()
    #ret = rzfile.namelist()

    # request.session.clear()

    dwnldLoc = "http://mrbrain.cs.jhu.edu" + userDefProjectDir.replace(' ','%20')
    return HttpResponse ( "Files available for download at " + dwnldLoc) # change to render of a page with a link to data result

  elif(not webargs):
    # request.session.clear()
    return django.http.HttpResponseBadRequest ("Expected web arguments to direct project correctly")

  else:
    # request.session.clear()
    return django.http.HttpResponseBadRequest ("Expected POST data, but none given")

################## TO DOs ########################
def download(request, webargs=None):
  # DM: TODO - Allow for data to be downloaded by the directory name/filename/projectName
  pass

#########################################
#	*******************		#
#	   GRAPH LOAD VIEW		#
#########################################
def graphLoadInv(request, webargs=None):
  ''' Form '''
  from glob import glob # Move
  # request.session.clear() # NEW

  if request.method == 'POST' and not webargs:
    form = GraphUploadForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():
      data = form.files['fileObj'] # get data
      request.session['invariants'] = form.cleaned_data['Select_Invariants_you_want_computed']

      request.session['graphsize'] = form.cleaned_data['Select_graph_size']

      dataDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
      makeDirIfNone([dataDir])

      # We got a zip
      if os.path.splitext(data.name)[1] == '.zip':

        writeBodyToDisk(data.read(), dataDir)
        # Get all graphs in the directory
        graphs = glob(os.path.join(dataDir,'*_fiber.mat'))
        graphs.extend(glob(os.path.join(dataDir,'*_bggr.mat')))
        graphs.extend(glob(os.path.join(dataDir,'*_smgr.mat')))

        request.session['graphInvariants'] = os.path.join(dataDir, 'graphInvariants')

        for G_fn in graphs:
          if request.session['graphsize'] == 'big':
            request.session['bgGrfn'] = G_fn
            lccfn = G_fn.split('_')[0] + '_concomp.mat'
            lccG = loadAdjMat(request.session['bgGrfn'], lccfn)

          elif request.session['graphsize'] == 'small':
            request.session['smGrfn'] = G_fn
            lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']

            runInvariants(lccG, request.session)
            print 'No project invariants %s complete...' % G_fn
          else:
            HttpResponse("<h2>The graph size is required to proceed.</h2>")
      else:
        return HttpResponse("<h2>The file you uploaded is not a zip see the instructions on the page before proceeding.</h2>")

      # request.session.clear() # NEW
      return HttpResponseRedirect("http://mrbrain.cs.jhu.edu"+ dataDir.replace(' ','%20')) # All spaces are replaced with %20 for urls

  if request.method == 'POST' and webargs:
    if (re.match(re.compile('(b|big)', re.IGNORECASE), webargs.split('/')[0])):
      request.session['graphsize'] = 'big'
    elif (re.match(re.compile('(s|small)', re.IGNORECASE), webargs.split('/')[0])):
       request.session['graphsize'] = 'small'
    else:
      return django.http.HttpResponseBadRequest("The graph size is required as a web argument")

    dataDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
    makeDirIfNone([dataDir])
    #if (request.body.name)
    uploadedZip = writeBodyToDisk(request.body, dataDir)[0]

    zipper.unzip(uploadedZip, dataDir) # Unzip the zip
    os.remove(uploadedZip) # Delete the zip)

    request.session['invariants'] = webargs.split('/')[1].split(',')

    graphs = glob(os.path.join(dataDir,'*_fiber.mat'))
    graphs.extend(glob(os.path.join(dataDir,'*_bggr.mat')))
    graphs.extend(glob(os.path.join(dataDir,'*_smgr.mat')))

    request.session['graphInvariants'] = os.path.join(dataDir, 'graphInvariants')

    for G_fn in graphs:
      if request.session['graphsize'] == 'big':
        request.session['bgGrfn'] = G_fn
        lccfn = G_fn.split('_')[0] + '_concomp.mat'
        lccG = loadAdjMat(request.session['bgGrfn'], lccfn)

      elif request.session['graphsize'] == 'small':
        request.session['smGrfn'] = G_fn
        lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']

      runInvariants(lccG, request.session)
      print 'Invariants computed with no project for: %s ...' % G_fn

    # request.session.clear()
    dwnldLoc = "http://mrbrain.cs.jhu.edu"+ dataDir.replace(' ','%20')
    return HttpResponse("View Data at: " + dwnldLoc)

  else:
    form = GraphUploadForm() # An empty, unbound form

  # Render the form
  return render_to_response(
      'graphupload.html',
      {'graphUploadForm': form},
      context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
  )

#########################################
#	*******************		#
#	  CONVERT GRAPH FORMAT		#
#########################################

def convert(request, webargs=None):
  ''' Form '''
  # request.session.clear() # NEW

  if (request.method == 'POST' and not webargs):
    form = ConvertForm(request.POST, request.FILES) # instantiating form
    if form.is_valid():

      baseDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('formUpload%a%d%b%Y_%H.%M.%S/', localtime()))
      saveDir = os.path.join(baseDir,'upload') # Save location of original uploads
      convertFileSaveLoc = os.path.join(baseDir,'converted') # Save location of converted data

      if not (os.path.exists(convertFileSaveLoc)):
        os.makedirs(convertFileSaveLoc)

      # ALTER TABLE ocpipeline_convertmodel MODIFY COLUMN filename TEXT;
      data = ConvertModel(filename = request.FILES['fileObj'])
      data._meta.get_field('filename').upload_to = saveDir # route files to correct location
      data.save()

      savedFile = os.path.join(saveDir, request.FILES['fileObj'].name)

      # If zip is uploaded
      if os.path.splitext(request.FILES['fileObj'].name)[1].strip() == '.zip':
        uploadedFiles = zipper.unzip(savedFile, saveDir)
        # Delete zip
        os.remove(savedFile)
      else:
        uploadedFiles = [savedFile]

      correctFileFormat, correctFileType = convertFiles(uploadedFiles, form.cleaned_data['Select_file_type'], \
                                                      form.cleaned_data['Select_conversion_format'], convertFileSaveLoc)

      if not (correctFileFormat):
        # request.session.clear()
        return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

        dwnldLoc = "http://mrbrain.cs.jhu.edu"+ convertFileSaveLoc.replace(' ','%20')
        # request.session.clear()
        return HttpResponseRedirect(dwnldLoc)

  # Programmtic API
  elif(request.method == 'POST' and webargs):
    # webargs is {fileType}/{toFormat}
    fileType = webargs.split('/')[0] # E.g 'cc', 'deg', 'triangle'
    toFormat =  (webargs.split('/')[1]).split(',')   # E.g 'mat', 'npy' or 'mat,csv'

    toFormat = list(set(toFormat)) # Eliminate duplicates if any exist

    # Make sure filetype is valid before doing any work
    if (fileType not in settings.VALID_FILE_TYPES.keys() and fileType not in settings.VALID_FILE_TYPES.values()):
      return HttpResponse('Invalid conversion type. Make sure toFormat is a valid type')

    # In case to format does not start with a '.'. Add if not
    for idx in range (len(toFormat)):
      if not toFormat[idx].startswith('.'):
        toFormat[idx] = '.'+toFormat[idx]

    baseDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime('progUpload%a%d%b%Y_%H.%M.%S/', localtime()))
    saveDir = os.path.join(baseDir,'upload') # Save location of original uploads
    convertFileSaveLoc = os.path.join(baseDir,'converted') # Save location of converted data

    if not os.path.exists(saveDir):
      os.makedirs(saveDir)

    if not os.path.exists(convertFileSaveLoc):
      os.makedirs(convertFileSaveLoc)

    uploadedFiles = writeBodyToDisk(request.body, saveDir)

    correctFileFormat, correctFileType = convertFiles(uploadedFiles, fileType, toFormat, convertFileSaveLoc)

    if not (correctFileType):
      # request.session.clear()
      return HttpResponse("[ERROR]: You did not enter a valid FileType.")
    if not (correctFileFormat):
      # request.session.clear()
      return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

    dwnldLoc = "http://mrbrain.cs.jhu.edu"+ convertFileSaveLoc.replace(' ','%20')
    # request.session.clear()
    return HttpResponse ( "Converted files available for download at " + dwnldLoc + " . The directory " +
            "may be empty if you try to convert to the same format the file is already in.") # change to render of a page with a link to data result

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

def processData(fiber_fn, roi_xml_fn, roi_raw_fn,graphs, graphInvariants, graphsize, run = False):
  '''
  Run graph building and other related scripts
  @param fiber_fn: fiber tract file
  @param roi_xml_fn: region of interest xml file
  @param roi_raw_fn: region of interest raw file

  @param graphs: Dir where biggraphs & smallgraphs are saved
  @param graphInvariants:  Dir where graph invariants are saved
  @param graphsize: the size of the graph 'big' or 'small'
  @param run: Whether or not to run processor intensive jobs. Default is - false so nothing is actually run
  '''
  if (run):
    import mrcap.svd as svd
    import mrcap.lcc as lcc
    print "Imported svd and lcc modules..."

  baseName = getFiberID(fiber_fn) #VERY TEMPORARY

  smGrfn = os.path.join(graphs, (baseName +'smgr.mat'))
  bgGrfn = os.path.join(graphs, (baseName +'bggr.mat'))

  if (run):
    ''' spawn subprocess to create small since its result is not necessary for processing '''
    #arguments = 'python ' + '/home/disa/MR-connectome/mrcap/gengraph.py /home/disa' + fiber_fn + ' /home/disa' + smallGraphOutputFileName +' /home/disa' + roi_xml_fn + ' /home/disa' + roi_raw_fn
    #arguments = 'python ' + '/Users/dmhembere44/MR-connectome/mrcap/gengraph.py /Users/dmhembere44' + fiber_fn + ' /Users/dmhembere44' + smallGraphOutputFileName + ' roixmlname=/Users/dmhembere44' + roi_xml_fn + ' roirawname=/Users/dmhembere44' + roi_raw_fn
    #subprocess.Popen(arguments,shell=True)
    if (graphsize == 'small'):
      ''' Run gengraph SMALL & save output '''
      print("Running Small gengraph....")
      gengraph.genGraph(fiber_fn, smGrfn, roi_xml_fn, roi_raw_fn, bigGraph=False)

    elif(graphsize == 'big'):
      ''' Run gengrah BIG & save output '''
      print("\nRunning Big gengraph....")
      gengraph.genGraph(fiber_fn, bgGrfn, roi_xml_fn, roi_raw_fn, bigGraph=True)
    else:
      print '[ERROR]: Graphsize Unkwown' # should never happen

  ''' Run LCC '''
  if not os.path.exists(os.path.join(graphInvariants,"LCC")):
    print "Making LCC directory"
    os.makedirs(os.path.join(graphInvariants,"LCC"))
  lccfn = os.path.join(graphInvariants,"LCC", (baseName + 'concomp.npy'))


  if (run):
    '''Should be big but we'll do small for now'''
    if (graphsize == 'big'):
      print "Running biggraph Largest connected component..."
      lcc.process_single_brain(roi_xml_fn, roi_raw_fn, bgGrfn, lccfn)
    if (graphsize == 'small'):
      print "Running smallgraph Largest connected component..."
      lcc.process_single_brain(roi_xml_fn, roi_raw_fn, smGrfn, lccfn)

  ''' Run Embed - SVD '''
  if not os.path.exists(os.path.join(graphInvariants,"SVD")):
    print "Making SVD directory"
    os.makedirs(os.path.join(graphInvariants,"SVD"))
  SVDfn = os.path.join(graphInvariants,"SVD" ,(baseName + 'embed.npy'))

  print("Running SVD....")
  roiBasename = os.path.splitext(roi_xml_fn)[0] # MAY NEED ADAPTATION

  if (run):
    if (graphsize == 'big'):
      print "Running SVD on biggraph"
      svd.embed_graph(lccfn, roiBasename, bgGrfn, SVDfn)
    if (graphsize == 'small'):
      print "Running SVD on smallgraph"
      svd.embed_graph(lccfn, roiBasename, smGrfn, SVDfn)

  print "Completed generating - graph, lcc & svd"
  return [ smGrfn, bgGrfn, lccfn, SVDfn ]

#########################################
#	*******************		#
#	     INVARIANTS			#
#########################################
def runInvariants(lccG, req_sess):
  '''
  @todo
  @param lccG: Sparse largest connected component adjacency matrix
  @param req_sess: current session dict containing session varibles
  '''

  if req_sess['graphsize'] == 'small':
    grfn = req_sess['smGrfn']
  elif req_sess['graphsize'] == 'big':
    grfn = req_sess['bgGrfn']
  else:
    return None # Should make things explode - TODO better handling

  # NOTE: The *_fn variable names are in accordance with settings.VALID_FILE_TYPES
  ss1_fn = None
  tri_fn = deg_fn =  ss2_fn = apl_fn = gdia_fn = cc_fn = numNodes = eigvlfn = eigvectfn = mad_fn = ss1_fn

  degDir = None
  ssDir = triDir = MADdir = eigvDir = degDir

  # Order the invariants correctly
  order = { 0:'ss1', 1:'tri', 2:'cc', 3:'mad', 4:'deg', 5:'eig',6:'ss2', 7:'apl', 8:'gdia' }
  invariants = []
  for i in range(len(order)):
    if order[i] in req_sess['invariants']:
      invariants.append(order[i])

  req_sess['invariants'] = invariants
  invariant_fns = {}

  #** ASSUMES ORDER OF INVARIANTS ARE PREDEFINED **#
  for inv in req_sess['invariants']:
    if inv == "ss1": # Get degree for free
      ssDir = os.path.join(req_sess['graphInvariants'],'ScanStat1')
      degDir = os.path.join(req_sess['graphInvariants'],'Degree')
      makeDirIfNone([ssDir, degDir])

      ss1_fn, deg_fn, numNodes = calcScanStat_Degree(G_fn = grfn,\
          G = lccG,  ssDir = ssDir, degDir = degDir) # Good to go

    if inv == "tri": # Get "Eigs" & "MAD" for free
      triDir = os.path.join(req_sess['graphInvariants'],'Triangle')
      MADdir = os.path.join(req_sess['graphInvariants'],'MAD')
      eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')

      if not (degDir):
        degDir = os.path.join(req_sess['graphInvariants'],'Degree')
        makeDirIfNone([triDir, MADdir, eigvDir, degDir])

        tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn =  eignTriLocal_deg_MAD(G_fn = grfn,\
            G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir, degDir = degDir) # Good to go
      else:
        makeDirIfNone([triDir, MADdir, eigvDir])

        tri_fn, eigvlfn, eigvectfn, mad_fn  = eignTriLocal_MAD(G_fn = grfn,\
            G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir) # Good to go

    if inv == "cc":  # We need "Deg" & "TriCnt"
      if not(eigvDir):
        eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')
      if not (degDir):
        degDir = os.path.join(req_sess['graphInvariants'],'Degree')
      if not (triDir):
        triDir = os.path.join(req_sess['graphInvariants'],'Triangle')

      if not (MADdir):
        MADdir = os.path.join(req_sess['graphInvariants'],'MAD')
      ccDir = os.path.join(req_sess['graphInvariants'],'ClustCoeff')

      makeDirIfNone([degDir, triDir, ccDir, eigvDir, MADdir])
      if (deg_fn and tri_fn):
        cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

      elif (deg_fn and (not tri_fn)):
        tri_fn, eigvlfn, eigvectfn, mad_fn = eignTriLocal_MAD(G_fn = grfn,\
            G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir) # Good to go
        cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

      elif (tri_fn and (not deg_fn)):
        deg_fn = calcDegree(G_fn = grfn, \
            G = lccG , degDir = degDir) # Good to go
        cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

      else:
        tri_fn, eigvlfn, eigvectfn, mad_fn = eignTriLocal_MAD(G_fn = grfn,\
            G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir) # Good to go
        deg_fn = calcDegree(G_fn = grfn, \
            G = lccG , degDir = degDir) # Good to go
        cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

    if inv == "mad": # Get "Eigs" for free
        if (tri_fn):
          pass
        else:
          MADdir = os.path.join(req_sess['graphInvariants'],'MAD')
          eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')
          makeDirIfNone([MADdir, eigvDir])

          mad_fn, eigvlfn, eigvectfn = calcMAD(G_fn = grfn, G = lccG , \
              MADdir = MADdir, eigvDir = eigvDir) # Good to go

    if inv == "deg": # Nothing for free
      if (deg_fn):
        pass
      else:
        degDir = os.path.join(req_sess['graphInvariants'],'Degree')
        makeDirIfNone([degDir])

        deg_fn = calcDegree(G_fn = grfn, \
            G = lccG ,  degDir = degDir) # Good to go

    if inv == "eig": # Nothing for free
      if (tri_fn):
        pass
      else:
        eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')
        makeDirIfNone([eigvDir])

        eigvlfn, eigvectfn = calcEigs(G_fn = grfn,\
                G = lccG , eigvDir = eigvDir)

    if inv == "ss2":
      #makeDirIfNone(dirPath)
      pass # TODO DM
    if inv == "apl":
      #makeDirIfNone(dirPath)
      pass # TODO DM
    if inv == "gdia":
      #makeDirIfNone(dirPath)
      pass # TODO DM

  for fn in [ ss1_fn, tri_fn, deg_fn, ss2_fn, apl_fn,  gdia_fn , cc_fn, ss1_fn]:
    if ss1_fn:
      invariant_fns['ss1'] = ss1_fn
    if tri_fn:
      invariant_fns['tri'] = tri_fn
    if deg_fn:
      invariant_fns['deg'] = deg_fn
    if ss2_fn:
      invariant_fns['ss2'] = ss2_fn
    if apl_fn:
      invariant_fns['apl'] = apl_fn
    if gdia_fn:
      invariant_fns['gdia'] = gdia_fn
    if cc_fn:
      invariant_fns['cc'] = cc_fn
    if mad_fn:
      invariant_fns['mad'] = mad_fn
    if eigvectfn:
      invariant_fns['eig'] = [eigvectfn, eigvlfn] # Note this
  return invariant_fns
