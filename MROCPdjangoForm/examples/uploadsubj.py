import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
 
import zipfile
import tempfile



from pprint import pprint

def main():

  parser = argparse.ArgumentParser(description='Upload a subject to MROCP.')
  parser.add_argument('url', action="store")
  parser.add_argument('fiberfile', action="store")
  parser.add_argument('roixmlfile', action="store")
  parser.add_argument('roirawfile', action="store")

  result = parser.parse_args()

  try:

    # Create a temporary file to store zip contents in memory
    tmpfile = tempfile.NamedTemporaryFile()
    zfile = zipfile.ZipFile ( tmpfile.name, "w" )

    zfile.write ( result.fiberfile, 'fiber.dat' )
    zfile.write ( result.roixmlfile, 'roixml.xml' )
    zfile.write ( result.roirawfile, 'roiraw.raw' )
    zfile.close()

    tmpfile.flush()
    tmpfile.seek(0)

#  Testing only: check the contents of a zip file.
#
#    rzfile = zipfile.ZipFile ( tmpfile.name, "r" )
#    ret = rzfile.printdir()
#    ret = rzfile.testzip()
#    ret = rzfile.namelist()

    
  except:
    print "All broke"
    sys.exit(0)

  try:
    req = urllib2.Request ( result.url, tmpfile.read() ) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()

