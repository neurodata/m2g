'''
@author : Disa Mhembere
Module to hold the views of a Django one-click MR-connectome pipeline
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
from ocpipeline.models import Document
from ocpipeline.models import ConvertModel

from ocpipeline.forms import DocumentForm
from ocpipeline.forms import OKForm
from ocpipeline.forms import DataForm
from ocpipeline.forms import GraphUploadForm
from ocpipeline.forms import ConvertForm
import mrpaths

''' Data Processing imports'''
from mrcap import gengraph as gengraph

import ocpipeline.filesorter as filesorter
import ocpipeline.zipper as zipper
import ocpipeline.createDirStruct as createDirStruct
import ocpipeline.convertTo as convertTo

from django.core.servers.basehttp import FileWrapper

import subprocess
from django.core.urlresolvers import get_script_prefix
from django.conf import settings

from time import strftime, localtime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

####################
## Graph Analysis ##
from computation.scanstat_degr import calcScanStat_Degree #as calcScanStat_Degree
from computation.clustCoeff import calcLocalClustCoeff #as calcLocalClustCoeff
from computation.loadAdjMatrix import loadAdjMat #as loadAdjMat
#from computation.triCount_MAD import eignTriLocal_MAD #as eignTriLocal_MAD
from computation.degree import calcDegree #as calcDegree
#from computation.MAD import calcMAD #as calcMAD
#from computation.Eigenvalues import calcEigs #as calcEigs
from computation.clustCoeff import calcLocalClustCoeff #as calcLocalClustCoeff
#from computation.triCount_deg_MAD import eignTriLocal_deg_MAD #as eignTriLocal_deg_MAD

#import scipy.sparse.linalg.eigen.arpack as arpack # THIS IS THE PROBLEM IMPORT

''' Little welcome message'''
def default(request):
    request.session.clear()
    return render_to_response('welcome.html')

''' Set project Dirs '''
def createProj(request, webargs=None):

    request.session.clear()
    request.session['lastView'] = 'createProj'

    ''' Form '''
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            userDefProjectName = form.cleaned_data['UserDefprojectName']
            site = form.cleaned_data['site']
            subject = form.cleaned_data['subject']
            session = form.cleaned_data['session']
            scanId = form.cleaned_data['scanId']

	    userDefProjectName = os.path.join(settings.MEDIA_ROOT, userDefProjectName) # Fully qualify
	    request.session['usrDefProjDir'] = os.path.join(userDefProjectName, site, subject, session, scanId)
	    request.session['scanId'] = scanId
	return HttpResponseRedirect(get_script_prefix()+'pipelineUpload') # Redirect after POST

    else:
        form = DataForm() # An unbound form

    return render(request, 'nameProject.html', {
        'form': form,
    })

''' Successful completion of task'''
def success(request):
    request.session['lastView'] = 'success'
    return render_to_response('success.html')

''' Upload files from user '''
def pipelineUpload(request, webargs=None):

    # If you haven't come through the create proj - start again
    if (('usrDefProjDir' not in request.session) or ('lastView' not in request.session)):
        return HttpResponseRedirect(get_script_prefix()+'create') # Return to start

    request.session['lastView'] = 'pipelineUpload'

    ''' Form '''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():

	    print "Uploading files..."

	    ''' Define data directory paths '''
	    request.session['derivatives'], request.session['rawdata'], request.session['graphs'],\
		request.session['graphInvariants'],request.session['images']= defDataDirs(request.session['usrDefProjDir'])

            newdoc = Document(docfile = request.FILES['docfile'])
	    newdoc._meta.get_field('docfile').upload_to = request.session['derivatives'] # route files to correct location

	    newdoc2 = Document(docfile = request.FILES['roi_raw_file'])
	    newdoc2._meta.get_field('docfile').upload_to = request.session['derivatives']

            newdoc3 = Document(docfile = request.FILES['roi_xml_file'])
            newdoc3._meta.get_field('docfile').upload_to = request.session['derivatives']

	    request.session['invariants'] = form.cleaned_data['Select_Invariants_you_want_computed']

            ''' Acquire fileNames '''
	    fiber_fn = form.cleaned_data['docfile'].name # get the name of the file input by user
            roi_raw_fn = form.cleaned_data['roi_raw_file'].name
            roi_xml_fn = form.cleaned_data['roi_xml_file'].name

            ''' Save files to temp location '''
            newdoc.save()
	    newdoc2.save()
            newdoc3.save()

	    print '\nSaving all files complete...'

            ''' Make appropriate dirs if they dont already exist '''
            createDirStruct.createDirStruct([request.session['derivatives'], request.session['rawdata'],\
		request.session['graphs'], request.session['graphInvariants'], request.session['images']])

            # Redirect to Processing page
        return HttpResponseRedirect(get_script_prefix()+'processInput')
    else:
        form = DocumentForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'pipelineUpload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

def processInputData(request):
    '''
    Extract File Name
    Determine what file corresponds to what for gengraph
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
	= processData(fiber_fn, roi_xml_fn, roi_raw_fn,request.session['graphs'], request.session['graphInvariants'], True)

    # Run ivariants here
    if len(request.session['invariants']) > 0:
	#lccG = loadAdjMat(request.session['smGrfn'], request.session['lccfn'], roiRootName = os.path.splitext(roi_xml_fn)[0])
	import scipy.io as sio
	lccG = sio.loadmat(request.session['smGrfn'])['fibergraph']
	runInvariants(lccG, request.session)

    return HttpResponseRedirect(get_script_prefix()+'confirmDownload')


def confirmDownload(request):

    if 'zipDwnld' in request.POST: # If zipDwnl option is chosen
	form = OKForm(request.POST)
	return HttpResponseRedirect(get_script_prefix()+'zipOutput') # Redirect after POST

    elif 'convToMatNzip' in request.POST: # If view dir structure option is chosen
	form = OKForm(request.POST)
	convertTo.convertLCCNpyToMat(request.session['lccfn'])
	convertTo.convertSVDNpyToMat(request.session['SVDfn'])
	# Incomplete
	#convertTo.convertGraphToCSV(request.session['smGrfn'])
	#convertTo.convertGraphToCSV(request.session['bgGrfn'])
	return HttpResponseRedirect(get_script_prefix()+'zipOutput')

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
    """Programmatic interface for uploading data"""
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

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu" + settings.MEDIA_ROOT + webargs
	return HttpResponse ( "Files available for download at " + dwnldLoc) # change to render of a page with a link to data result

    elif(not webargs):
	return django.http.HttpResponseBadRequest ("Expected web arguments to direct project correctly")

    else:
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
    if request.method == 'POST':
        form = GraphUploadForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():
	    data = form.files['fileObj'] # get data
	    request.session['invariants'] = form.cleaned_data['Select_Invariants_you_want_computed']

	    # We got a zip
	    if os.path.splitext(data.name)[1] == '.zip':
		rzfile = putDataInTempZip(data.read())
		uploadedFiles = writeTempZipToDisk(rzfile,os.path.join(settings.MEDIA_ROOT, \
					'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()) ))

		for fn in uploadedFiles:
		    #runNoProjInvariants(rzfile.read(name), request.session['invariants'])
		    print 'No proj inv %s complete...' % name

	    else:
		#path = default_storage.save(os.path.join(settings.MEDIA_ROOT, 'tmp', strftime("projectStamp%a%d%b%Y_%H.%M.%S/", localtime()), data.name), ContentFile(data.read()))
		print '\nSaving %s complete...' % data.name
		runNoProjInvariants(ContentFile(data.read()), request.session['invariants'])

        return HttpResponseRedirect(get_script_prefix()+'success') # STUB
    else:
        form = GraphUploadForm() # An empty, unbound form

    # Render the form
    return render_to_response(
        'graphupload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

#########################################
#	*******************		#
#	  CONVERT GRAPH FORMAT		#
#########################################

def convert(request, webargs=None):

    ''' Form '''
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
	    return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ convertFileSaveLoc
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
	    return HttpResponse("[ERROR]: You did not enter a valid FileType.")
	if not (correctFileFormat):
	    return HttpResponse("[ERROR]: You do not have any files with the correct extension for conversion")

	dwnldLoc = "http://www.mrbrain.cs.jhu.edu"+ convertFileSaveLoc
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
    graphs - Dir where biggraphs & smallgraphs are saved
    graphInvariants - Dir where graph invariants are saved
    run - Default is false so nothing is actually run
    '''
    if (run):
	import mrcap.svd as svd
	import mrcap.lcc as lcc

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
    lccfn = os.path.join(graphInvariants, (baseName + 'concomp.npy'))

    if (run):
	'''Should be big but we'll do small for now'''
	#**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, bgGrfn, lccfn)
	lcc.process_single_brain(roi_xml_fn, roi_raw_fn, smGrfn, lccfn)

    ''' Run Embed - SVD '''
    SVDfn = os.path.join(graphInvariants, (baseName + 'embed.npy'))

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
    lccG - Sparse largest connected component adjacency matrix
    req_sess - current session dict containing session varibles
    '''
    SS1fn = None
    TriCntfn = Degfn =  SS2fn = APLfn = GDiafn = CCfn = numNodes = SS1fn

    degDir = None
    ssDir = triDir = MADdir = eigvDir = degDir

    # Since we predefine the index order in forms.py
    for inv in req_sess['invariants']:
	if inv == "SS1": # Get degree for free
	    ssDir = os.path.join(req_sess['derivatives'],'ScanStat1')
	    degDir = os.path.join(req_sess['derivatives'],'Degree')
	    makeDirIfNone([ssDir, degDir])

	    SS1fn, Degfn, numNodes = calcScanStat_Degree(G_fn = req_sess['smGrfn'],\
		G = lccG,  ssDir = ssDir, degDir = degDir)

	if inv == "TriCnt": # Get "Eigs" & "MAD" for free
	    triDir = os.path.join(req_sess['derivatives'],'Triangle')
	    MADdir = os.path.join(req_sess['derivatives'],'MAD')
	    eigvDir = os.path.join(req_sess['derivatives'],'Eigen')

	    if not (degDir):
		degDir = os.path.join(req_sess['derivatives'],'Degree')
		makeDirIfNone([triDir, MADdir, eigvDir, degDir])

		TriCntfn, Degfn =  eignTriLocal_deg_MAD(G_fn = req_sess['smGrfn'],\
				    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir, degDir = degDir)
	    else:
		makeDirIfNone([triDir, MADdir, eigvDir])

		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)

	if inv == "CC":  # We need "Deg" & "TriCnt"
	    if not (degDir):
		degDir = os.path.join(req_sess['derivatives'],'Degree')
	    if not (triDir):
		triDir = os.path.join(req_sess['derivatives'],'Triangle')
	    ccDir = os.path.join(req_sess['derivatives'],'ClustCoeff')

	    makeDirIfNone([degDir, triDir, ccDir])
	    if (Degfn and TriCntfn):
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    elif (Degfn and (not TriCntfn)):
		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    elif (TriCntfn and (not Degfn)):
		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    else:
		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)
		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	if inv == "MAD": # Get "Eigs" for free
	    if (TriCntfn):
		pass
	    else:
		MADdir = os.path.join(req_sess['derivatives'],'MAD')
		eigvDir = os.path.join(req_sess['derivatives'],'Eigen')
		makeDirIfNone([MADdir, eigvDir])

		calcMAD(G_fn = req_sess['smGrfn'], G = lccG , \
		    MADdir = MADdir, eigvDir = eigvDir)

	if inv == "Deg": # Nothing for free
	    if (Degfn):
		pass
	    else:
		degDir = os.path.join(req_sess['derivatives'],'Degree')
		makeDirIfNone([degDir])

		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG ,  degDir = degDir)

	if inv == "Eigs": # Nothing for free
	    if (TriCntfn):
		pass
	    else:
		eigvDir = os.path.join(req_sess['derivatives'],'Eigen')
		makeDirIfNone([eigvDir])

		calcEigs(G_fn = req_sess['smGrfn'],\
			G = lccG , eigvDir = eigvDir)

	if inv == "SS2":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM
	if inv == "APL":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM
	if inv == "GDia":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM

#########################################
#	*******************		#
#	INVARIANTS NO PROJECT		#
#########################################
def runNoProjInvariants(lccG, req_sess_invs):
    '''
    lccG - Sparse largest connected component adjacency matrix
    req_sess - current session dict containing session varibles
    '''

    print "STUB!"
    '''
    SS1fn = None
    TriCntfn = Degfn =  SS2fn = APLfn = GDiafn = CCfn = numNodes

    # Since we predefine the index order in forms.py
    for inv in req_sess['invariants']:
	if inv == "SS1": # Get degree for free
	    ssDir = os.path.join(req_sess['derivatives'],'ScanStat1')
	    degDir = os.path.join(req_sess['derivatives'],'Degree')
	    makeDirIfNone([ssDir, degDir])

	    SS1fn, Degfn, numNodes = calcScanStat_Degree(G_fn = req_sess['smGrfn'],\
		G = lccG,  ssDir = ssDir, degDir = degDir)

	if inv == "TriCnt": # Get "Eigs" & "MAD" for free
	    triDir = os.path.join(req_sess['derivatives'],'Triangle')
	    MADdir = os.path.join(req_sess['derivatives'],'MAD')
	    eigvDir = os.path.join(req_sess['derivatives'],'Eigen')

	    if not (degDir):
		degDir = os.path.join(req_sess['derivatives'],'Degree')
		makeDirIfNone([triDir, MADdir, eigvDir, degDir])

		TriCntfn, Degfn =  eignTriLocal_deg_MAD(G_fn = req_sess['smGrfn'],\
				    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir, degDir = degDir)
	    else:
		makeDirIfNone([triDir, MADdir, eigvDir])

		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)

	if inv == "CC":  # We need "Deg" & "TriCnt"
	    if not (degDir):
		degDir = os.path.join(req_sess['derivatives'],'Degree')
	    if not (triDir):
		triDir = os.path.join(req_sess['derivatives'],'Triangle')
	    ccDir = os.path.join(req_sess['derivatives'],'ClustCoeff')

	    makeDirIfNone([degDir, triDir, ccDir])
	    if (Degfn and TriCntfn):
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    elif (Degfn and (not TriCntfn)):
		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    elif (TriCntfn and (not Degfn)):
		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	    else:
		TriCntfn = eignTriLocal_MAD(G_fn = req_sess['smGrfn'],\
		    G = lccG, triDir = triDir, MADdir = MADdir, eigvDir = eigvDir)
		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG , degDir = degDir)
		calcLocalClustCoeff(Degfn, TriCntfn, ccDir = ccDir)

	if inv == "MAD": # Get "Eigs" for free
	    if (TriCntfn):
		pass
	    else:
		MADdir = os.path.join(req_sess['derivatives'],'MAD')
		eigvDir = os.path.join(req_sess['derivatives'],'Eigen')
		makeDirIfNone([MADdir, eigvDir])

		calcMAD(G_fn = req_sess['smGrfn'], G = lccG , \
		    MADdir = MADdir, eigvDir = eigvDir)

	if inv == "Deg": # Nothing for free
	    if (Degfn):
		pass
	    else:
		degDir = os.path.join(req_sess['derivatives'],'Degree')
		makeDirIfNone([degDir])

		Degfn = calcDegree(G_fn = req_sess['smGrfn'], \
		    G = lccG ,  degDir = degDir)

	if inv == "Eigs": # Nothing for free
	    if (TriCntfn):
		pass
	    else:
		eigvDir = os.path.join(req_sess['derivatives'],'Eigen')
		makeDirIfNone([eigvDir])

		calcEigs(G_fn = req_sess['smGrfn'],\
			G = lccG , eigvDir = eigvDir)

	if inv == "SS2":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM
	if inv == "APL":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM
	if inv == "GDia":
	    #makeDirIfNone(dirPath)
	    pass # TODO DM
    '''


'''********************* Standalone Methods  *********************'''
def makeDirIfNone(dirPathList):
    '''
    Create a dir specified by dirPath
    Failure usual due to permissions issues
    dirPathList - A 'list' of the full paths of directory(ies) to be created
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
    fiberFileName - is a tract file name with naming convention '[filename]_fiber.dat'
	where filename may vary but _fiber.dat may not.
    This returns fiberfn's full path less the 'fiber.dat' portion
    '''
    return fiberFileName.partition('_')[0]

def defDataDirs(projectDir):
    '''
    Define all the paths to the data product directories
    projectDir - the fully qualified path of the project directory
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
    fiberfn - the dMRI streamline file in format {filename}_fiber.dat
    '''
    if fiberfn.endswith('/'):
	fiberfn = fiberfn[:-1] # get rid of trailing slash
    return fiberfn.split('/')[-1][:-9]

def writeBodyToDisk(data, saveDir):
    '''
    @param data the data to be written to file
    @param saveDir - the location of where data is to be written
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

def putDataInTempZip(data):
    '''
    Put data in a temporary zipped file
    data - any writable sum of bytes
    '''
    tmpfile = tempfile.NamedTemporaryFile()
    tmpfile.write ( data )
    tmpfile.flush()
    tmpfile.seek(0)
    print 'Temporary file created...'
    return zipfile.ZipFile ( tmpfile.name, "r" )

def writeTempZipToDisk(rzfile, saveDir):
    '''
    Extract & save zipped files
    rzfile - A zipfile
    saveDir - the location where it should be saved
    '''
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
    @param uploadedFiles - array with all file names of uploaded files
    @param fileType -
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
