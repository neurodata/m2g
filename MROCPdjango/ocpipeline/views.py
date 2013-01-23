#!/usr/bin/python

'''
@author : Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: Module to hold the views of a Django one-click MR-connectome pipeline
'''

import os, sys, re
#os.environ['MPLCONFIGDIR'] = '/tmp/'
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
from forms import OKForm
from forms import GraphUploadForm
from forms import ConvertForm
from forms import BuildGraphForm

import mrpaths

''' Data Processing imports'''
from mrcap import gengraph as gengraph

import filesorter as filesorter
import zipper as zipper
import createDirStruct as createDirStruct
import convertTo as convertTo

from django.core.servers.basehttp import FileWrapper

import subprocess
from django.core.urlresolvers import get_script_prefix
from django.conf import settings

from time import strftime, localtime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

####################
## Graph Analysis ##
####################

from computation.scanstat_degr import calcScanStat_Degree
from computation.clustCoeff import calcLocalClustCoeff
from computation.loadAdjMatrix import loadAdjMat
#from computation.triCount_MAD import eignTriLocal_MAD #****
from computation.degree import calcDegree
#from computation.MAD import calcMAD #****
#from computation.eigen import calcEigs #****
from computation.clustCoeff import calcLocalClustCoeff
#from computation.triCount_deg_MAD import eignTriLocal_deg_MAD #****

#import scipy.sparse.linalg.eigen.arpack as arpack # THIS IS THE PROBLEM IMPORT

''' Little welcome message'''
def default(request):
    request.session.clear()
    return render_to_response('welcome.html')

def buildGraph(request):
    request.session.clear()

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

	    userDefProjectName = os.path.join(settings.MEDIA_ROOT, userDefProjectName) # Fully qualify
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
        {'form': form},
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
	    return render_to_response('pipelineUpload.html', {'form': form}, context_instance=RequestContext(request)) # Missing file for processing Gengraph

    baseName = fiber_fn[:-9] #MAY HAVE TO CHANGE

    ''' Fully qualify file names'''
    fiber_fn = os.path.join(request.session['derivatives'], fiber_fn)
    roi_raw_fn = os.path.join(request.session['derivatives'], roi_raw_fn)
    roi_xml_fn = os.path.join(request.session['derivatives'], roi_xml_fn)

    request.session['smGrfn'], request.session['bgGrfn'], request.session['lccfn'],request.session['SVDfn'] \
	= processData(fiber_fn, roi_xml_fn, roi_raw_fn,request.session['graphs'], request.session['graphInvariants'],True)

    # Run ivariants here
    if len(request.session['invariants']) > 0:
	print "Computing invariants"
	#lccG = loadAdjMat(request.session['bgGrfn], request.session['lccfn'], roiRootName = os.path.splitext(roi_xml_fn)[0])
	import scipy.io as sio
	lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']
	request.session['invariant_fns'] =  runInvariants(lccG, request.session)
    return HttpResponseRedirect(get_script_prefix()+'confirmdownload')

#################################
#################################

def getDirFromFilename(filename):
    '''
    @summary: Get the directort location of a file
    @param filename: the full filename of the file in question
    @return: the directory of the file passed in as a param
    '''
    path = ''
    for part in filename.split('/')[:-1]:
	path += part + '/'
    return path

#################################
#################################

def confirmDownload(request):

    if 'zipDwnld' in request.POST: # If zipDwnl option is chosen
	form = OKForm(request.POST)
	return HttpResponseRedirect(get_script_prefix()+'zipOutput') # Redirect after POST

    elif 'convToMatNzip' in request.POST: # If view dir structure option is chosen
	form = OKForm(request.POST)
	convertTo.convertLCCNpyToMat(request.session['lccfn'])
	convertTo.convertSVDNpyToMat(request.session['SVDfn'])

	import pdb; pdb.set_trace()

	# Conversion of all files
	for inv in request.session['invariant_fns'].keys():
	    if isinstance(request.session['invariant_fns'][inv], list):
		for fn in request.session['invariant_fns'][inv]:
		    convertTo.convertAndSave(fn, 'mat', getDirFromFilename(fn), inv)
	    else:
		convertTo.convertAndSave(request.session['invariant_fns'][inv], 'mat', \
					 getDirFromFilename(request.session['invariant_fns'][inv]) , inv)

	# TODO: DM
	#convertTo.convertGraphToCSV(request.session['smGrfn'])
	#convertTo.convertGraphToCSV(request.session['bgGrfn'])

	# Tests here
	return HttpResponseRedirect(get_script_prefix()+'zipoutput')

    elif 'getProdByDir' in request.POST: # If view dir structure option is chosen
	form = OKForm(request.POST)

	dataUrlTail = request.session['usrDefProjDir']
	request.session.clear() # Very important

	return HttpResponseRedirect('http://mrbrain.cs.jhu.edu' + dataUrlTail)

    elif 'convToMatNgetByDir' in request.POST: # If view dir structure option is chosen
	form = OKForm(request.POST)
	convertTo.convertLCCNpyToMat(request.session['lccfn'])
	convertTo.convertSVDNpyToMat(request.session['SVDfn'])

	# Incomplete
	#convertTo.convertGraphToCSV(request.session['smGrfn'])
	#convertTo.convertGraphToCSV(request.session['bgGrfn'])

	dataUrlTail = request.session['usrDefProjDir']
	request.session.clear() # Very important

	return HttpResponseRedirect('http://mrbrain.cs.jhu.edu' + dataUrlTail)

    else:
	form = OKForm()
    return render(request, 'confirmDownload.html', {
        'form': form,
    })


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

    request.session.clear() # Very Important
    ''' Send it '''
    return response

def upload(request, webargs=None):
    """
    Programmatic interface for uploading data
    @param request: the request object

    @param webargs: POST data with userDefProjectName, site, subject, session, scanId, addmatNcsv info
    """
    request.session.clear() # NEW

    if (webargs and request.method == 'POST'):

	[userDefProjectName, site, subject, session, scanId, addmatNcsv] = webargs.split('/') # [:-1] # Add to server version

	userDefProjectDir = os.path.join(settings.MEDIA_ROOT, userDefProjectName, site, subject, session, scanId)

	''' Define data directory paths '''
	derivatives, rawdata,  graphs, graphInvariants, images = defDataDirs(userDefProjectDir)

	''' Make appropriate dirs if they dont already exist '''
	createDirStruct.createDirStruct([derivatives, rawdata, graphs, graphInvariants, images])
	print 'Directory structure created...'

	''' Get data from request.body '''

	tmpfile = tempfile.NamedTemporaryFile()
	tmpfile.write ( request.body )
	tmpfile.flush()
	tmpfile.seek(0)
	rzfile = zipfile.ZipFile ( tmpfile.name, "r" )

	print 'Temporary file created...'

	''' Extract & save zipped files '''
	uploadFiles = []
	for name in (rzfile.namelist()):

	    outfile = open(os.path.join(derivatives, name.split('/')[-1]), 'wb') # strip name of source folders if in file name
	    outfile.write(rzfile.read(name))
	    outfile.flush()
	    outfile.close()
	    uploadFiles.append(os.path.join(derivatives, name.split('/')[-1])) # add to list of files
	    print name + " written to disk.."

	  # Check which file is which
	roi_xml_fn, fiber_fn, roi_raw_fn = filesorter.checkFileExtGengraph(uploadFiles) # Check & sort files

	''' Data Processing '''
	smGrfn, bgGrfn, lccfn, SVDfn \
	  = processData(fiber_fn, roi_xml_fn, roi_raw_fn,graphs, graphInvariants, True) # Change to false to not process anything

	''' If optional .mat graph invariants & .csv graphs '''
	if re.match(re.compile('(y|yes)$',re.I),addmatNcsv):
	    convertTo.convertLCCNpyToMat(lccfn)
	    convertTo.convertSVDNpyToMat(SVDfn)
	    # Incomplete
	    #convertTo.convertGraphToCSV(smGrfn)
	    #convertTo.convertGraphToCSV(bgGrfn)

	#ret = rzfile.printdir()
	#ret = rzfile.testzip()
	#ret = rzfile.namelist()

	request.session.clear() # NEW

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu" + settings.MEDIA_ROOT + webargs
	return HttpResponse ( "Files available for download at " + dwnldLoc) # change to render of a page with a link to data result

    elif(not webargs):
	request.session.clear() # NEW
	return django.http.HttpResponseBadRequest ("Expected web arguments to direct project correctly")

    else:
	request.session.clear() # NEW
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
    request.session.clear() # NEW

    if request.method == 'POST' and not webargs:
        form = GraphUploadForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():
	    data = form.files['fileObj'] # get data
	    request.session['invariants'] = form.cleaned_data['Select_Invariants_you_want_computed']

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
		    #***request.session['bgGrfn'] = G_fn
		    #***lccfn = G_fn.split('_')[0] + '_concomp.mat'
		    #***roiRootName = G_fn.split('_')[0] + '_roi'
		    #***lccG = loadAdjMat(request.session['bgGrfn'], lccfn, roiRootName = roiRootName)

		    request.session['smGrfn'] = G_fn
		    import scipy.io as sio
		    lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']

		    runInvariants(lccG, request.session)
		    print 'No project invariants %s complete...' % G_fn
	    else:
		return HttpResponse("<h2>The file you uploaded is not a zip see the instructions on the page before proceeding.</h2>")

	    request.session.clear() # NEW
	    dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ dataDir

	    return HttpResponseRedirect(get_script_prefix()+'success') # STUB

    if request.method == 'POST' and webargs:
	dataDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
	makeDirIfNone([dataDir])
	#if (request.body.name)
	uploadedZip = writeBodyToDisk(request.body, dataDir)[0]

	zipper.unzip(uploadedZip, dataDir) # Unzip the zip
	os.remove(uploadedZip) # Delete the zip

	request.session['invariants'] = webargs.split(',')

	graphs = glob(os.path.join(dataDir,'*_fiber.mat'))
	graphs.extend(glob(os.path.join(dataDir,'*_bggr.mat')))
	graphs.extend(glob(os.path.join(dataDir,'*_smgr.mat')))

	request.session['graphInvariants'] = os.path.join(dataDir, 'graphInvariants')

	for G_fn in graphs:
	    #***request.session['bgGrfn'] = G_fn
	    #***lccfn = G_fn.split('_')[0] + '_concomp.mat'
	    #***roiRootName = G_fn.split('_')[0] + '_roi'
	    #***lccG = loadAdjMat(request.session['bgGrfn'], lccfn, roiRootName = roiRootName)

	    request.session['smGrfn'] = G_fn
	    import scipy.io as sio
	    lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']

	    runInvariants(lccG, request.session)
	    print 'No project invariants %s complete...' % G_fn

	request.session.clear() # NEW
	dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ dataDir
	return HttpResponse("View Data at: " + dwnldLoc) # STUB

    else:
        form = GraphUploadForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'graphupload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

#    else:
#	projDir = os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()))
#	request.session['smGrfn'] = default_storage.save(os.path.join(projDir, data.name), ContentFile(data.read()))
#	print '\nSaving %s complete...' % data.name
#
#	request.session['graphInvariants'] = os.path.join(projDir, 'graphInvariants')
#
#	#lccG = loadAdjMat(request.session['bgGrfn'], request.session['lccfn'], roiRootName = os.path.splitext(roi_xml_fn)[0])
#	import scipy.io as sio
#	lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']
#	runInvariants(lccG, request.session)

#########################################
#	*******************		#
#	  CONVERT GRAPH FORMAT		#
#########################################

def convert(request, webargs=None):
    ''' Form '''
    request.session.clear() # NEW

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
	    request.session.clear() # NEW
	    return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ convertFileSaveLoc
	request.session.clear() # NEW
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
	    request.session.clear() # NEW
	    return HttpResponse("[ERROR]: You did not enter a valid FileType.")
	if not (correctFileFormat):
	    request.session.clear() # NEW
	    return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ convertFileSaveLoc
	request.session.clear() # NEW
	return HttpResponse ( "Converted files available for download at " + dwnldLoc + " . The directory " +
		"may be empty if you try to convert to the same format the file is already in.") # change to render of a page with a link to data result

    else:
        form = ConvertForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'convertupload.html',
        {'form': form},
        context_instance=RequestContext(request))

#########################################
#	*******************		#
#	   PROCESS DATA			#
#########################################
def processData(fiber_fn, roi_xml_fn, roi_raw_fn,graphs, graphInvariants, run = False):
    '''
    Run graph building and other related scripts
    @param fiber_fn: fiber tract file
    @param roi_xml_fn: region of interest xml file
    @param roi_raw_fn: region of interest raw file

    @param graphs: Dir where biggraphs & smallgraphs are saved
    @param graphInvariants:  Dir where graph invariants are saved
    @param run: Whether or not to run processor intensive jobs. Default is - false so nothing is actually run
    '''
    if (run):
	import mrcap.svd as svd
	import mrcap.lcc as lcc
	print "Imported svd and lcc modules..."

    baseName = getFiberID(fiber_fn) #VERY TEMPORARY

    '''Run gengraph SMALL & save output'''
    print("Running Small gengraph....")
    smGrfn = os.path.join(graphs, (baseName +'smgr.mat'))

    if (run):
	''' spawn subprocess to create small since its result is not necessary for processing '''
	#arguments = 'python ' + '/home/disa/MR-connectome/mrcap/gengraph.py /home/disa' + fiber_fn + ' /home/disa' + smallGraphOutputFileName +' /home/disa' + roi_xml_fn + ' /home/disa' + roi_raw_fn
	#arguments = 'python ' + '/Users/dmhembere44/MR-connectome/mrcap/gengraph.py /Users/dmhembere44' + fiber_fn + ' /Users/dmhembere44' + smallGraphOutputFileName + ' roixmlname=/Users/dmhembere44' + roi_xml_fn + ' roirawname=/Users/dmhembere44' + roi_raw_fn
	#subprocess.Popen(arguments,shell=True)

	gengraph.genGraph(fiber_fn, smGrfn, roi_xml_fn, roi_raw_fn)

    ''' Run gengrah BIG & save output '''
    print("\nRunning Big gengraph....")
    bgGrfn = os.path.join(graphs, (baseName +'bggr.mat'))
    #**gengraph.genGraph(fiber_fn, bgGrfn, roi_xml_fn ,roi_raw_fn, True)

    ''' Run LCC '''
    if not os.path.exists(os.path.join(graphInvariants,"LCC")):
	print "Making LCC directory"
	os.makedirs(os.path.join(graphInvariants,"LCC"))
    lccfn = os.path.join(graphInvariants,"LCC", (baseName + 'concomp.npy'))

    if (run):
	'''Should be big but we'll do small for now'''
	#**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, bgGrfn, lccfn)
	lcc.process_single_brain(roi_xml_fn, roi_raw_fn, smGrfn, lccfn)

    ''' Run Embed - SVD '''
    if not os.path.exists(os.path.join(graphInvariants,"SVD")):
	print "Making SVD directory"
	os.makedirs(os.path.join(graphInvariants,"SVD"))
    SVDfn = os.path.join(graphInvariants,"SVD" ,(baseName + 'embed.npy'))

    print("Running SVD....")

    roiBasename = str(roi_xml_fn[:-4]) # WILL NEED ADAPTATION

    if (run):
	#**svd.embed_graph(lccfn, roiBasename, bgGrfn, SVDfn)
	svd.embed_graph(lccfn, roiBasename, smGrfn, SVDfn)

    print "Generating graph, lcc & svd complete!"
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

	    ss1_fn, deg_fn, numNodes = calcScanStat_Degree(G_fn = req_sess['smGrfn'],\
		G = lccG,  ssDir = ssDir, degDir = degDir) # Good to go

	if inv == "tri": # Get "Eigs" & "MAD" for free
	    triDir = os.path.join(req_sess['graphInvariants'],'Triangle')
	    MADdir = os.path.join(req_sess['graphInvariants'],'MAD')
	    eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')

	    if not (degDir):
		degDir = os.path.join(req_sess['graphInvariants'],'Degree')
		makeDirIfNone([triDir, MADdir, eigvDir, degDir])

		tri_fn, deg_fn, MAD_fn, eigvl_fn, eigvect_fn =  eignTriLocal_deg_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir, degDir = degDir) # Good to go
	    else:
		makeDirIfNone([triDir, MADdir, eigvDir])

		tri_fn, eigvlfn, eigvectfn, mad_fn  = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
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
		tri_fn, eigvlfn, eigvectfn, mad_fn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir) # Good to go
		cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

	    elif (tri_fn and (not deg_fn)):
		deg_fn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir) # Good to go
		cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

	    else:
		tri_fn, eigvlfn, eigvectfn, mad_fn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir) # Good to go
		deg_fn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir) # Good to go
		cc_fn = calcLocalClustCoeff(deg_fn, tri_fn, ccDir = ccDir) # Good to go

	if inv == "mad": # Get "Eigs" for free
	    if (tri_fn):
		pass
	    else:
		MADdir = os.path.join(req_sess['graphInvariants'],'MAD')
		eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')
		makeDirIfNone([MADdir, eigvDir])

		mad_fn, eigvlfn, eigvectfn = calcMAD(G_fn = req_sess['smGrfn'], G = lccG , \
		    MADdir = MADdir, eigvDir = eigvDir) # Good to go

	if inv == "deg": # Nothing for free
	    if (deg_fn):
		pass
	    else:
		degDir = os.path.join(req_sess['graphInvariants'],'Degree')
		makeDirIfNone([degDir])

		deg_fn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG ,  degDir = degDir) # Good to go

	if inv == "eig": # Nothing for free
	    if (tri_fn):
		pass
	    else:
		eigvDir = os.path.join(req_sess['graphInvariants'],'Eigen')
		makeDirIfNone([eigvDir])

		eigvlfn, eigvectfn = calcEigs(G_fn = req_sess['smGrfn'],\
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
	    invariant_fns['eig'] = eigvectfn, eigvlfn # Note this
    return invariant_fns


'''********************* Standalone Methods  *********************'''
def makeDirIfNone(dirPathList):
    '''
    Create a dir specified by dirPathList. Failure usual due to permissions issues.

    @param dirPathList: A 'list' of the full paths of directory(ies) to be created
    '''
    for dirPath in dirPathList:
	try:
	    if not (os.path.exists(dirPath)):
		os.makedirs(dirPath)
		print "%s directory made successfully" % dirPath
	    else:
		print "%s directory already exists" % dirPath
	except:
	    print "[ERROR] while attempting to create %s" % dirPath
	    sys.exit(-1)

def getFiberPath(fiberFileName):
    '''
    This returns fiberfn's full path less the 'fiber.dat' portion

    @param fiberFileName - is a tract file name with naming convention '[filename]_fiber.dat'
	where filename may vary but _fiber.dat may not.
    '''
    return fiberFileName.partition('_')[0]

def defDataDirs(projectDir):
    '''
    Define all the paths to the data product directories

    @param projectDir: the fully qualified path of the project directory
    '''
    derivatives = os.path.join(projectDir, 'derivatives')
    rawdata = os.path.join(projectDir, 'rawdata')
    graphs = os.path.join(projectDir, 'graphs')
    graphInvariants = os.path.join(projectDir, 'graphInvariants')
    images = os.path.join(projectDir, 'images')

    return [derivatives, rawdata, graphs, graphInvariants, images]

def getFiberID(fiberfn):
    '''
    Assumptions about the data made here as far as file naming conventions

    @param fiberfn: the dMRI streamline file in format {filename}_fiber.dat
    '''
    if fiberfn.endswith('/'):
	fiberfn = fiberfn[:-1] # get rid of trailing slash
    return fiberfn.split('/')[-1][:-9]

def writeBodyToDisk(data, saveDir):
    '''
    Write the requests body to disk

    @param data: the data to be written to file
    @param saveDir: the location of where data is to be written

    @return a list with the names of the uplaoded files
    '''
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write ( data )
    tmpfile.flush()
    tmpfile.seek(0)
    rzfile = zipfile.ZipFile ( tmpfile.name, "r" )

    print 'Temporary file created...'

    ''' Extract & save zipped files '''
    uploadFiles = []
    for name in (rzfile.namelist()):
	outfile = open(os.path.join(saveDir, name.split('/')[-1]), 'wb') # strip name of source folders if in file name
	outfile.write(rzfile.read(name))
	outfile.flush()
	outfile.close()
	uploadFiles.append(os.path.join(saveDir, name.split('/')[-1])) # add to list of files
	print name + " written to disk.."
    return uploadFiles

def convertFiles(uploadedFiles, fileType , toFormat, convertFileSaveLoc):
    '''
    @todo

    @param uploadedFiles: array with all file names of uploaded files
    @param fileType
    @param toFormat -
    @param convertFileSaveLoc -
    @return correctFileFormat - check if at least one file has the correct format
    @return correctFileType - check if file type is legal
    '''
    for file_fn in uploadedFiles:
	# determine type of the file
	if (os.path.splitext(file_fn)[1] in ['.mat','.csv','.npy']):
	    correctFileFormat = True
	    if (fileType == 'fg' or fileType == 'fibergraph'):
		correctFileType = True
		pass # TODO : DM
	    elif( fileType == 'lcc' or fileType == 'lrgstConnComp'):
		correctFileType = True
		pass # TODO : DM
	    elif (fileType in settings.VALID_FILE_TYPES.keys() or fileType in settings.VALID_FILE_TYPES.values()):
		# Check if file format is the same as the toFormat
		if (os.path.splitext(file_fn)[1] in toFormat):
		    toFormat.remove(os.path.splitext(file_fn)[1])
		if (len(toFormat) == 0):
		    pass # No work to be done here
		else:
		    correctFileType = True
		    convertTo.convertAndSave(file_fn, toFormat, convertFileSaveLoc, fileType) # toFormat is a list
    return correctFileFormat, correctFileType
