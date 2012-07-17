'''
@author : Disa Mhembere
Module to hold the views of a Django one-click MR-connectome pipeline
'''
import os, sys

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

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
inputRoi_xml = ''
inputFiber_dat = ''
inputRoi_raw = ''

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

def hello(request):
    global projectName
    global userDefProjectDir
    global userDefProjectName
    global zipFileName
    global scanId
    
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
    

def success(request):
    return render_to_response('success.html')   

def pipelineUpload(request):
    global uploadDirPath
    global projectName # temp project Name
    global userDefProjectDir
    global derivatives
    global rawdata
    global graphs
    global graphInvariants
    global tempDirPath       
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES) # instantiating form
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc2 = Document(docfile = request.FILES['roi_raw_file'])
            newdoc3 = Document(docfile = request.FILES['roi_xml_file'])
            projectName = newdoc.getProjectName() # Update the global project name so I can output in matching folder name****
            uploadDirPath = tempDirPath + projectName # Update upload directory for new project
            
            ''' Acquire fileNames'''
            fiber_fn = form.cleaned_data['docfile'].name # get the name of the file input by user
            roi_raw_fn = form.cleaned_data['roi_raw_file'].name
            roi_xml_fn = form.cleaned_data['roi_xml_file'].name
            
            
            ''' Save files to temp location'''
            newdoc.save()
            newdoc2.save()
            newdoc3.save()
            print '\nSaving all files complete...\n'
            
            ''' Make appropriate dirs if they dont already exist'''
            dataProds = ['derivatives/', 'rawdata/', 'graphs/', 'graphInvariants/']
            
            derivatives = userDefProjectDir + 'derivatives/'
            rawdata = userDefProjectDir + 'rawdata/'
            graphs = userDefProjectDir + 'graphs/'
            graphInvariants = userDefProjectDir + 'graphInvariants/'
            
            for folder in dataProds:
                if not os.path.exists(folder):
                    os.makedirs(userDefProjectDir + folder)
                    
            ''' Move files to appropriate location '''
            
            #import pdb; pdb.set_trace();
            
            uploadedFiles = [ os.path.join(uploadDirPath,fiber_fn), os.path.join(uploadDirPath, roi_raw_fn)
                             ,os.path.join(uploadDirPath,roi_xml_fn)]
            
            for thefile in uploadedFiles:
                move(thefile, derivatives) # Where to save derivatives
            
            ''' Delete temp project folder'''
            rmtree(tempDirPath + projectName)
            
            # Redirect to Processing page
        return HttpResponseRedirect('/processInput')  #return HttpResponseRedirect('http://google.com')
    else:
        form = DocumentForm() # An empty, unbound form
        
    # Render the form
    return render_to_response(
        'pipelineUpload.html',
        {'form': form},
        context_instance=RequestContext(request) # Some failure to input data & returns a key signaling what is requested
    )

def processInputData(request):
    
    '''Extract File Names
    	Determine what file corresponds to what for gengraph
    '''
    global inputRoi_xml
    global inputFiber_dat
    global inputRoi_raw
    
    global derivatives    
    filesInUploadDir = os.listdir(derivatives)
    
    inputRoi_xml, inputFiber_dat, inputRoi_raw = filesorter.checkFileExtGengraph(filesInUploadDir) # Check & sort files
    
    for fileName in [inputRoi_xml, inputFiber_dat, inputRoi_raw]:
        if fileName == "": # Means a file is missing from i/p
            return render_to_response('pipelineUpload.html', {'form': form}, context_instance=RequestContext(request)) # Missing file for processing Gengraph    
    
    # Fully qualify file names
    inputRoi_xml = derivatives + inputRoi_xml
    inputFiber_dat = derivatives + inputFiber_dat
    inputRoi_raw = derivatives + inputRoi_raw
    
    global graphs  # let function see path for final graph residence
    global smallGraphOutputFileName # Change global name for small graph o/p file name so all methods can see it
    global processingScriptDirPath
    
    '''Run gengrah SMALL & save output'''
    print("Running Small gengraph....")
    smallGraphOutputFileName = graphs + 'SmallGraph.mat'
    arguments = 'python ' + processingScriptDirPath + 'gengraph.py ' + inputFiber_dat + ' ' + smallGraphOutputFileName +' ' + inputRoi_xml + ' ' + inputRoi_raw 
    #******subprocess.Popen(arguments,shell=True) # spawn subprocess to run gengraph
    gengraph.genGraph(inputFiber_dat, smallGraphOutputFileName, inputRoi_xml ,inputRoi_raw)
    
    ''' Run gengrah BIG & save output '''
    global bigGraphOutputFileName  # Change global name for small graph o/p file name
    print("Running Big gengraph....")
    bigGraphOutputFileName = graphs +  'BigGraph.mat'
    #**gengraph.genGraph(inputFiber_dat, bigGraphOutputFileName, inputRoi_xml ,inputRoi_raw, True)
    
    ''' Run LCC '''
    global graphInvariants
    lccOutputFileName = graphInvariants + 'LCC.npy'
    
    figDirPath = graphInvariants + 'figures/'

    if not os.path.exists(figDirPath):
        os.makedirs(figDirPath)

    '''Should be big but we'll do small for now'''
    #**lcc.process_single_brain(inputRoi_xml, inputRoi_raw, bigGraphOutputFileName, lccOutputFileName)
    #**lcc.process_single_brain(inputRoi_xml, inputRoi_raw, smallGraphOutputFileName, lccOutputFileName)
    
    ''' Run Embed - SVD '''
    global embedSVDOutputFileName
    embedSVDOutputFileName = graphInvariants + 'EMBED.npy'
    
    print("\nRunning SVD....")
    roiBaseName = str(inputRoi_xml[:-4])
    #**svd.embed_graph(lccOutputFileName, roiBaseName, bigGraphOutputFileName, embedSVDOutputFileName)
    #**svd.embed_graph(lccOutputFileName, roiBaseName, smallGraphOutputFileName, embedSVDOutputFileName)
    return HttpResponseRedirect('/confirmDownload/')

def confirmDownload(request):
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

def postProcessedData(request):
    '''
    Compress data products to single zip for upload
    '''
    global scanId
    global userDefProjectDir
    
    ''' Zip routine '''
    temp = zipper.zipFilesFromFolders(userDefProjectDir, scanId)
    
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = ('attachment; filename='+ scanId +'.zip')
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
