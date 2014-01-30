import urllib2
import argparse
import sys
import os

import zipfile
import tempfile

import webbrowser
import re

def getFiberID(fiberfn):
  '''
  Assumptions about the data made here as far as file naming conventions

  @param fiberfn: the dMRI streamline file in format {filename}_fiber.dat
  '''
  if fiberfn.endswith('/'):
    fiberfn = fiberfn[:-1] # get rid of trailing slash

  if re.match(re.compile(r'.+_fiber$'), os.path.splitext(fiberfn.split('/')[-1])[0]):
    return(os.path.splitext(fiberfn.split('/')[-1])[0]).split('_')[0] + '_'
  else:
    return os.path.splitext(fiberfn.split('/')[-1])[0] + '_'

def main():

  parser = argparse.ArgumentParser(description='Upload a multiple subjects to MROCP via a single dir that must match bg1/MRN. Base url -> http://www.mrbrain.cs.jhu.edu/disa/upload')
  parser.add_argument('url', action="store", help='url must be http://mrbrain.cs.jhu.edu/disa/upload/{projectName}/{site}/{subject}/{session}')
  parser.add_argument('graphsize', action="store", help= 'size of the graph. s OR b where s= smallgraph OR b = biggraph')
  parser.add_argument('fiberDir', action="store", help = 'the path of the directory containing fiber tract files')
  parser.add_argument('roiDir', action="store", help = 'the path of the directory containing ROI files')
  parser.add_argument('-i', '--invariants', action="store", help='OPTIONAL: comma separated list of invariant types. E.g cc,tri,deg,mad for \
                      clustering coefficient, triangle count, degree & maximum average degree')

  parser.add_argument('-a', '--auto', action="store_true", help="Use this flag if you want a browser session to open up with the result automatically")

  result = parser.parse_args()

  for fiber_fn in os.listdir(result.fiberDir):
    if not fiber_fn.startswith('.'): # get rid of meta files & hidden ones
      fiber_fn = os.path.join(result.fiberDir,fiber_fn)

      if not (os.path.exists(fiber_fn)):
        print "[ERROR]: fiber_fn '%s' not found!" % fiber_fn
        sys.exit(0)

      roi_xml_fn = os.path.join(result.roiDir, getFiberID(fiber_fn) + 'roi.xml') # Edit appropriately for file naming convention
      roi_raw_fn = os.path.join(result.roiDir, getFiberID(fiber_fn) + 'roi.raw') # Edit appropriately for file naming convention

      if not (os.path.exists(roi_xml_fn) or os.path.exists(roi_raw_fn)):
        print "[ERROR]: Rois not found! Check that filename is in form basename_roi.xml or basename_roi.raw"
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
      result.graphsize = result.graphsize if result.graphsize.endswith('/') else result.graphsize + '/'

      ''' VERY IMPORTANT TO NOTE HOW TO BUILD THE URL '''
      if result.invariants:
        callUrl = result.url + getFiberID(fiber_fn)[:-1]+ '/' + result.graphsize + result.invariants
      else:
        callUrl = result.url + getFiberID(fiber_fn)[:-1]+ '/' + result.graphsize

      print "Calling url: " + callUrl

      try:
        req = urllib2.Request ( callUrl, tmpfile.read() )  # concatenate project with assigned scanID & call url
        response = urllib2.urlopen(req)
      except urllib2.URLError, e:
        print "Failed URL", result.url
        print "Error %s" % (e.read())
        sys.exit(0)

  the_page = response.read()
  print "Here is parent directory:\n====> " + the_page

  if result.auto:
    ''' Optional: Open up a tab/window in your browser to view results'''
    webbrowser.open(the_page.split(' ')[5][:-len(the_page.split('/')[-1])]) # little string manipulation

if __name__ == "__main__":
  main()
