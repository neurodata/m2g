import urllib2
import argparse
import sys
import os

import zipfile
import tempfile

import webbrowser

def getFiberID(fiberfn):
    '''
    Assumptions about the data made here as far as file naming conventions
    '''
    if fiberfn.endswith('/'):
      fiberfn = fiberfn[:-1] # get rid of trailing slash
    return fiberfn.split('/')[-1][:-9]

def main():

  parser = argparse.ArgumentParser(description='Upload a mulitple subjects to MROCP via a single dir that must match bg1/MRN\
		   . Base url -> http://www.mrbrain.cs.jhu.edu/disa/upload')
  parser.add_argument('url', action="store", help='url must be in the form: {project}/{site}/{subject}/{session}/yes|no\      , where the last param is either \'yes\' or \'no\', but not both. \'yes\' adds .mat files for graph invariant result & \	    .csv for graphs, \'no\' does not')
  parser.add_argument('dataDir', action="store", help ='Data directory must have a fiber\
                      subdirectory with tract files & an roi subdirectory with rois')
  
  result = parser.parse_args()
    
  fiberDir = os.path.join(result.dataDir, 'fiber')
  roiDir = os.path.join(result.dataDir, 'roi')
  
  for fiber_fn in os.listdir(fiberDir):
    fiber_fn = os.path.join(fiberDir,fiber_fn)
    
    if not (os.path.exists(fiber_fn)):
      print "Either fiber_fn not found!"
      sys.exit(0)
      
    roi_xml_fn = os.path.join(roiDir, getFiberID(fiber_fn) + 'roi.xml')
    roi_raw_fn = os.path.join(roiDir, getFiberID(fiber_fn) + 'roi.raw')
      
    if not (os.path.exists(roi_xml_fn) or os.path.exists(roi_raw_fn)):
      print "Rois not found!"
      sys.exit(0)
    
    # Create a temporary file to store zip contents in memory
    tmpfile = tempfile.NamedTemporaryFile()
    zfile = zipfile.ZipFile ( tmpfile.name, "w" )

    zfile.write(fiber_fn)
    zfile.write(roi_xml_fn)
    zfile.write(roi_raw_fn)
    zfile.close()

    tmpfile.flush()
    tmpfile.seek(0)

#  Testing only: check the contents of a zip file.
#
#    rzfile = zipfile.ZipFile ( tmpfile.name, "r" )
#    ret = rzfile.printdir()
#    ret = rzfile.testzip()
#    ret = rzfile.namelist()
#    import pdb; pdb.set_trace()
    
    result.url = result.url if result.url.endswith('/') else result.url + '/' # 
    
    try:
      req = urllib2.Request ( result.url + getFiberID(fiber_fn)[:-1], tmpfile.read() )  # concatenate project with assigned scanID & call url
      response = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print "Failed URL", result.url
      print "Error %s" % (e.read()) 
      sys.exit(0)

    the_page = response.read()
    print "Success with id %s" % the_page
  
  ''' Open up a tab in your browser to view results'''
  redir = '/'
  for Dir in result.url.split('/')[-4:]:
    if (Dir != result.url.split('/')[-1]):
      redir += Dir + '/'
    else:
      redir += Dir
  
  webbrowser.open('http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects' + redir)

if __name__ == "__main__":
  main()
