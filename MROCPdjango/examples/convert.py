import urllib2
import argparse
import sys
import os
import scipy.io as sio

import zipfile
import tempfile

import webbrowser

''' RESTful API '''

def main():

  parser = argparse.ArgumentParser(description='Upload and convert a graph from graphml,ncol,edgelist,lgl,pajek,graphdb,numpy,mat to graphml,ncol,edgelist,lgl,pajek,dot,gml,leda object. Base url -> http://mrbrain.cs.jhu.edu/disa/convert')

  parser.add_argument('url', action="store", help='url must be in the form http://mrbrain.cs.jhu.edu/disa/convert/{inFormat}/{outFormat}. Example {inFormat}: graphml | ncol | edgelist | lgl | pajek | graphdb | numpy | mat \
                      .{outFormat} can be a comma separated list of the following e.g graphml,ncol,edgelist,lgl,pajek,dot,gml,leda')

  parser.add_argument('fileToConvert', action="store", help="The file you want to convert. Can to single graph of zip file with multiple graphs. Zip graphs not folders!")
  parser.add_argument('-a', '--auto', action="store_true", help="Use this flag if you want a browser session to open up with the result automatically")

  result = parser.parse_args()

  if not (os.path.exists(result.fileToConvert)):
    print "Invalid file name. Check the filename: " + result.fileToConvert
    sys.exit()
  else:
    print "Loading file into memory.."

  tmpfile = tempfile.NamedTemporaryFile()
  zfile = zipfile.ZipFile ( tmpfile.name, "w" )

  zfile.write ( result.fileToConvert)
  zfile.close()

  tmpfile.flush()
  tmpfile.seek(0)

  try:
    req = urllib2.Request ( result.url, tmpfile.read())
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read())
    sys.exit(0)

  msg = response.read() # Use this response better
  print msg

  if result.auto:
    ''' Open up a tab in your browser to view results'''
    webbrowser.open(msg.split(' ')[6]) # This would change

if __name__ == "__main__":
  main()
