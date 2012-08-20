import urllib2
import argparse
import sys
 
import zipfile
import tempfile

def main():

  parser = argparse.ArgumentParser(description='Upload a subject to MROCP.')
  parser.add_argument('url', action="store", help='url must be in the form  upload/{project}/{site}/{subject}/{session}/{scanID}')
  parser.add_argument('fiberfile', action="store")
  parser.add_argument('roixmlfile', action="store")
  parser.add_argument('roirawfile', action="store")

  result = parser.parse_args()

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
    req = urllib2.Request ( result.url, tmpfile.read() ) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", result.url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page
  
  ''' Open up a tab in your browser to view results'''
  redir = '/'
  for Dir in result.url.split('/')[-5:]:
    if (Dir != result.url.split('/')[-1]):
      redir += Dir + '/'
    else:
      redir += Dir
  import webbrowser
  webbrowser.open('http://www.openconnecto.me/data/projects/disa/OCPprojects' + redir)

  
if __name__ == "__main__":
  main()

