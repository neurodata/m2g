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

  parser = argparse.ArgumentParser(description='Upload and convert a file between .mat, .npy, .csv bject. Base url -> http://mrbrain.cs.jhu.edu/disa/convert')
  parser.add_argument('fileToConvert', action="store", help="The full file name of the file to be converted")
  parser.add_argument('url', action="store", help='url must be in the form http://mrbrain.cs.jhu.edu/disa/convert/{fileType}/{toFormat}. Example {fileType} values fg|[fibergraph], cc|[clustCoeff] \
                      {toFormat} can be a comma separated list e.g mat,npy,csv')

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

  ''' Open up a tab in your browser to view results'''
  webbrowser.open(msg.split(' ')[6]) # This would change

if __name__ == "__main__":
  main()
