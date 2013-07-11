import urllib2
import argparse
import sys

import zipfile
import tempfile

import webbrowser


''' RESTful API '''

def main():

  parser = argparse.ArgumentParser(description='Upload a subject to MROCP. Base url -> http://mrbrain.cs.jhu.edu/disa/upload')
  parser.add_argument('url', action="store", help='url must have NO SPACES & must be in the form  http://mrbrain.cs.jhu.edu/disa/upload/{projectName}/{site}/{subject}/{session}/{scanID}/{s|b} where s= smallgraph OR b = biggraph')
  parser.add_argument('-i', '--invariants', action="store", help='OPTIONAL: comma separated list of invariant types. E.g cc,tri,deg,mad for \
                      clustering coefficient, triangle count, degree & maximum average degree')

  parser.add_argument('fiberfile', action="store")
  parser.add_argument('roixmlfile', action="store")
  parser.add_argument('roirawfile', action="store")

  parser.add_argument('-a', '--auto', action="store_true", help="Use this flag if you want a browser session to open up with the result automatically")

  result = parser.parse_args()

  result.url = result.url if result.url.endswith('/') else result.url + '/' #

  try:

    # Create a temporary file to store zip contents in memory
    tmpfile = tempfile.NamedTemporaryFile()
    zfile = zipfile.ZipFile ( tmpfile.name, "w" )

    zfile.write ( result.fiberfile)
    zfile.write ( result.roixmlfile )
    zfile.write ( result.roirawfile)
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

  except:
    print "Invalid file name. Check the filenames: " + result.fiberfile,  result.roixmlfile,  result.roirawfile
    sys.exit(0)

  try:
    if (result.invariants is not None):
      req = urllib2.Request ( result.url + result.invariants , tmpfile.read() ) # Important to concatenate these in this order
    else:
      req = urllib2.Request ( result.url, tmpfile.read() )

    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read())
    sys.exit(0)

  the_page = response.read()
  print '/n' +  the_page

  if result.auto:
    ''' Optional: Open up a tab/window in your browser to view results'''
    webbrowser.open(the_page.split(' ')[5])

if __name__ == "__main__":
  main()
