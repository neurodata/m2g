import urllib2
import argparse
import sys
import os
import scipy.io as sio
import zipfile
import tempfile

import webbrowser

from glob import glob

''' RESTful API '''

def main():

  parser = argparse.ArgumentParser(description='Upload and convert a directory of files .mat, .npy, .csv files. Base url -> http://mrbrain.cs.jhu.edu/disa/convert')
  parser.add_argument('dirToConvert', action="store", help="Name of DIRECTORY NOT ZIP containing files to be converted")
  parser.add_argument('url', action="store", help='url must be in the form http://mrbrain.cs.jhu.edu/disa/convert/{fileType}/{toFormat}. Example {fileType} values fg|[fibergraph], cc|[clustCoeff] \
                      {toFormat} can be a comma separated list e.g mat,npy,csv')

  parser.add_argument('-a', '--auto', action="store_true", help="Use this flag if you want a browser session to open up with the result automatically")

  result = parser.parse_args()

  if not (os.path.exists(result.dirToConvert)):
    print "Invalid directory name. Check the directory name: " + result.dirToConvert
    sys.exit()
  else:
    print "Loading file into memory.."

  tmpfile = tempfile.NamedTemporaryFile()
  zfile = zipfile.ZipFile ( tmpfile.name, "w" )

  for fileToConvert in glob(os.path.join(result.dirToConvert,'*')):
    zfile.write ( fileToConvert )

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
    webbrowser.open(msg.split(' ')[6]) # Comment this to disable auto open in a browser

if __name__ == "__main__":
  main()
