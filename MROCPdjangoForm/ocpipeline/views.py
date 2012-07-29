'''
@author : Disa Mhembere
Module to hold the views of a Django one-click MR-connectome pipeline
'''
import os, sys

from django.shortcuts import render_to_response
from django.shortcuts import render

#from django.shortcuts import redirect

from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.core.files import File        # For programmatic file upload

from ocpipeline.models import Document
from ocpipeline.forms import DocumentForm
from ocpipeline.forms import OKForm
from ocpipeline.forms import DataForm
import mrpaths

from django.http import HttpResponse

''' Data Processing imports'''
#import mrcap.gengraph as gengraph
from mrcap import gengraph as gengraph

#**import ocpipeline.mrcap.svd as svd
#**from ocpipeline.mrcap import lcc

import ocpipeline.filesorter as filesorter
import ocpipeline.zipper as zipper
import ocpipeline.createDirStruct as createDirStruct

from django.core.servers.basehttp import FileWrapper

import subprocess
from shutil import move, rmtree # For moving files

'''
Global Paths
'''

uploadDirPath = '/data/projects/disa/OCPprojects/' # Global path to files that are uploaded by users
tempDirPath = uploadDirPath + 'temp/'
processingScriptDirPath = os.path.abspath(os.path.curdir) + "/ocpipeline/mrcap/" # Global path to location of processing code

'''
Global file Names all initialized to an empty string
'''
roi_xml_fn = ''
fiber_fn = ''
roi_raw_fn = ''

smallGraphOutputFileName = '' # fileName of output of gengraph for a small graph
bigGraphOutputFileName = '' # fileName of output of gengraph for a big graph
lccOutputFileName = ''
embedSVDOutputFileName = ''

''' To hold each type of file available for download'''
derivatives = ''    # _fiber.dat, _roi.xml, _roi.raw
rawdata = ''        # none yet
graphs = ''         # biggraph, smallgraph
graphInvariants = ''# LCC.npy (largest connected components), EMBED.ny (Single Value Decomposition)
scanId = ''

projectName ='' # Initial save location of derivatives
userDefProjectName = ''
userDefProjectDir = ''
zipFileName = ''

''' Little welcome message'''
def default(request):
    return render_to_response('welcome.html')

def hello(request, webargs=None):
    global projectName
    global userDefProjectDir
    global userDefProjectName
    global zipFileName
    global scanId
    
    ''' Programmatic''' 
    if (webargs):
        [userDefProjectName, site, subject, session, scanId] = request.path.split('/')[2:7] # This will always be true
    
        zipFileName = userDefProjectName
        userDefProjectName = uploadDirPath + userDefProjectName + '/' # Fully qualify
        userDefProjectDir =  userDefProjectName + site +'/'+ subject+'/'+ session+'/'+ scanId+'/'
        
        return HttpResponseRedirect('/pipelineUpload/') # Redirect after POST
    
    ''' Form '''
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            userDefProjectName = form.cleaned_data['UserDefprojectName']
            zipFileName = userDefProjectName
            site = form.cleaned_data['site']
            subject = form.cleaned_data['subject']
            session = form.cleaned_data['session']
            scanId = form.cleaned_data['scanId']
            
            userDefProjectName = uploadDirPath + userDefProjectName + '/' # Fully qualify
            
            userDefProjectDir =  userDefProjectName + site +'/'+ subject+'/'+ session+'/'+ scanId+'/'
            
        return HttpResponseRedirect('/pipelineUpload/') # Redirect after POST
    else:
        form = DataForm() # An unbound form
   
    return render(request, 'nameProject.html', {
        'form': form,
    })

''' Successful completion of task'''
def success(request):
    return render_to_response('success.html')   

def pipelineUpload(request, webargs=None):
    global uploadDirPath
    global projectName # temp project Name
    global userDefProjectDir
    global derivatives
    global rawdata
    global graphs
    global graphInvariants
    global tempDirPath
    
    ''' Programmatic Version
        webargs should be fully qualified name of track file e.g /data/files/name_fiber.dat
        Assumption is naming convention is name_fiber.dat, name_roi.dat, name_roi.xml, where
        'name' is the same in all cases
    ''' 
    if (webargs):
        fiber_fn = request.path[15:] # Directory where
        if fiber_fn[-1] == '/': # in case of trailing backslash
            fiber_fn = fiber_fn[:-1]
            
        '''Assume directory & naming structure matches braingraph1's: "/data/projects/MRN/base" structure'''
        roi_raw_fn = roi_xml_fn = '/'
        
        for i in fiber_fn.split('/')[1:-2]:
            roi_raw_fn += i + '/'
            roi_xml_fn += i + '/'
            
        basename = fiber_fn.split('/')[-1][:-9]
        roi_raw_fn += 'roi/' +  basename +'roi.raw'
        roi_xml_fn += 'roi/' +  basename +'roi.xml'
        
        for files in [fiber_fn, roi_xml_fn, roi_raw_fn] : # Names of files
            doc = Document() # create a new Document for each file
            with open(files, 'rb') as doc_file: # Open file for reading
                doc.docfile.save(files, File(doc_file), save=True) # Save upload files
                doc.save()
        
	''' Just the filename with no path info '''
	fiber_fn = fiber_fn.split('/')[-1] 
	roi_raw_fn = roi_raw_fn.split('/')[-1]
	roi_xml_fn = roi_xml_fn.split('/')[-1]

        projectName = doc.getProjectName() # Update the global project name so I can output in matching folder name
        tempFolder = tempDirPath + projectName # Update upload directory for new project
            
        ''' Make appropriate dirs if they dont already exist'''
        dataProds = ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/']
        
        derivatives = userDefProjectDir + 'derivatives/'
        rawdata = userDefProjectDir + 'rawdata/'
        graphs = userDefProjectDir + 'graphs/'
        graphInvariants = userDefProjectDir + 'graphInvariants/'
        createDirStruct.createDirStruct(userDefProjectDir, tempFolder, derivatives, tempDirPath, [fiber_fn, roi_raw_fn, roi_xml_fn]);
	
	#import pdb; pdb.set_trace();
	
	return HttpResponse(processInputData(request.GET, webargs))

    ''' Form '''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc2 = Document(docfile = request.FILES['roi_raw_file'])
            newdoc3 = Document(docfile = request.FILES['roi_xml_file'])
            projectName = newdoc.getProjectName() # Update the global project name so I can output in matching folder name
            tempFolder = tempDirPath + projectName # Update upload directory for new project
            
            ''' Acquire fileNames '''
            fiber_fn = form.cleaned_data['docfile'].name # get the name of the file input by user
            roi_raw_fn = form.cleaned_data['roi_raw_file'].name
            roi_xml_fn = form.cleaned_data['roi_xml_file'].name
            
            ''' Save files to temp location '''
            newdoc.save()
            newdoc2.save()
            newdoc3.save()
            print '\nSaving all files complete...\n'
               
            ''' Make appropriate dirs if they dont already exist '''
            dataProds = ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/'] # **
            
            derivatives = userDefProjectDir + 'derivatives/'
            rawdata = userDefProjectDir + 'rawdata/'
            graphs = userDefProjectDir + 'graphs/'
            graphInvariants = userDefProjectDir + 'graphInvariants/'
            
            createDirStruct.createDirStruct(userDefProjectDir, tempFolder, derivatives, tempDirPath,[fiber_fn, roi_raw_fn, roi_xml_fn]);
            
            # Redirect to Processing page
        return HttpResponseRedirect('/processInput')
    else:
        form = DocumentForm() # An empty, unbound form
        
    # Render the form
    return render_to_response(
        'pipelineUpload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

def processInputData(request, webargs = None):
    '''
    Extract File Name
    Determine what file corresponds to what for gengraph
    '''
    global roi_xml_fn
    global fiber_fn
    global roi_raw_fn
    global derivatives
    
    filesInUploadDir = os.listdir(derivatives)
    
    roi_xml_fn, fiber_fn, roi_raw_fn = filesorter.checkFileExtGengraph(filesInUploadDir) # Check & sort files
    
    for fileName in [roi_xml_fn, fiber_fn, roi_raw_fn]:
        if fileName == "": # Means a file is missing from i/p
            return render_to_response('pipelineUpload.html', {'form': form}, context_instance=RequestContext(request)) # Missing file for processing Gengraph    
    
    # Fully qualify file names
    roi_xml_fn = derivatives + roi_xml_fn
    fiber_fn = derivatives + fiber_fn
    roi_raw_fn = derivatives + roi_raw_fn
    
    global graphs  # let function see path for final graph residence
    global smallGraphOutputFileName # Change global name for small graph o/p file name so all methods can see it
    global processingScriptDirPath
    
    '''Run gengrah SMALL & save output'''
    print("Running Small gengraph....")
    smallGraphOutputFileName = graphs + 'SmallGraph.mat'
    arguments = 'python ' + processingScriptDirPath + 'gengraph.py ' + fiber_fn + ' ' + smallGraphOutputFileName +' ' + roi_xml_fn + ' ' + roi_raw_fn 
    #******subprocess.Popen(arguments,shell=True) # spawn subprocess to run gengraph
    #gengraph.genGraph(fiber_fn, smallGraphOutputFileName, roi_xml_fn ,roi_raw_fn)
    
    ''' Run gengrah BIG & save output '''
    global bigGraphOutputFileName  # Change global name for small graph o/p file name
    print("Running Big gengraph....")
    bigGraphOutputFileName = graphs +  'BigGraph.mat'
    #**gengraph.genGraph(fiber_fn, bigGraphOutputFileName, roi_xml_fn ,roi_raw_fn, True)
    
    ''' Run LCC '''
    global graphInvariants
    lccOutputFileName = graphInvariants + 'LCC.npy'
    
    figDirPath = graphInvariants + 'figures/'

    if not os.path.exists(figDirPath):
        os.makedirs(figDirPath)

    '''Should be big but we'll do small for now'''
    #**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, bigGraphOutputFileName, lccOutputFileName)
    #**lcc.process_single_brain(roi_xml_fn, roi_raw_fn, smallGraphOutputFileName, lccOutputFileName)
    
    ''' Run Embed - SVD '''
    global embedSVDOutputFileName
    embedSVDOutputFileName = graphInvariants + 'EMBED.npy'
    
    print("\nRunning SVD....")
    roiBaseName = str(roi_xml_fn[:-4])
    #**svd.embed_graph(lccOutputFileName, roiBaseName, bigGraphOutputFileName, embedSVDOutputFileName)
    #**svd.embed_graph(lccOutputFileName, roiBaseName, smallGraphOutputFileName, embedSVDOutputFileName)
    
    if (webargs):
	print "\nProcessInputData has webargs"
	#return HttpResponseRedirect('confirmDownload/')
	#return redirect('/zipOutput') # Zipout & allow client to download
	request.path = u'/zipOutput/'
	return HttpResponse(zipProcessedData(request))
	    
    return HttpResponseRedirect('/confirmDownload/')




def confirmDownload(request, webargs = None):
    if request.method == 'POST': # If form is submitted
        form = OKForm(request.POST)
        if form.is_valid():
            pass # Maybe log response in database
        return HttpResponseRedirect('/zipOutput') # Redirect after POST
    else:
        form = OKForm() # An unbound form
    return render(request, 'confirmDownload.html', {
        'form': form,
    })

def zipProcessedData(request):
    '''
    Compress data products to single zip for upload
    '''
    
    global scanId
    global userDefProjectDir
    
    #import pdb; pdb.set_trace();
    
    ''' Zip routine '''
    temp = zipper.zipFilesFromFolders(userDefProjectDir, scanId)
    
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = ('attachment; filename='+ scanId +'.zip')
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    
    return response

