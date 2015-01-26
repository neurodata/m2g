#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
@author: Disa Mhembere
@organization: Johns Hopkins University
@contact: disa@jhu.edu

@summary: A module to Create a ZIP file on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory.
"""

import os
import tempfile, zipfile
import argparse
from util import get_genus

def zipFilesFromFolders(dirName = None, multiTuple = []):
  '''
  @deprecated
  @param dirName: any folder
  '''
  temp = tempfile.TemporaryFile(dir="/data/pytmp")
  myzip = zipfile.ZipFile(temp ,'w', zipfile.ZIP_DEFLATED, allowZip64=True)

  if (multiTuple):
    for dirName in multiTuple:
      if dirName[0] != '.': # ignore metadata
        dirName = os.path.join(multiTuple, dirName)
        filesInOutputDir = os.listdir(dirName)

        for thefolder in filesInOutputDir:
          if thefolder[0] != '.': # ignore metadata
              dataProdDir = os.path.join(dirName, thefolder)
              for thefile in os.listdir(dataProdDir):
                filename =  os.path.join(dataProdDir, thefile)
                myzip.write(filename, thefile) # second param of write determines name output
                print "Compressing: " + thefile
    myzip.close()
    return temp


  filesInOutputDir = os.listdir(dirName)

  for thefolder in filesInOutputDir:
    if thefolder[0] != '.': # ignore metadata
      dataProdDir = os.path.join(dirName, thefolder)
      for thefile in os.listdir(dataProdDir):
        filename =  os.path.join(dataProdDir, thefile)
        myzip.write(filename, thefile) # second param of write determines name output
        print "Compressing: " + thefile

  myzip.close()
  return temp

def zipup(directory, zip_file, todisk=None):
  '''
  Write a zipfile from a directory

  @param dir: the path to directory to be zipped
  @type dir: string

  @param zip_file: name of zip file
  @type zip_file: string

  @param todisk: specify path if you want the zip written to disk as well
  @type todisk: string
  '''
  zip_file = tempfile.TemporaryFile(dir="/data/pytmp")

  zipf = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
  root_len = len(os.path.abspath(directory))
  for root, dirs, files in os.walk(directory):
    archive_root = os.path.abspath(root)[root_len:] # = archive_root = os.path.basename(root)
    for f in files:
      fullpath = os.path.join(root, f)
      archive_name = os.path.join(archive_root, f)
      print "Compressing: " + f
      zipf.write(fullpath, archive_name, zipfile.ZIP_DEFLATED) # (from, to_in_archive, format)
  zipf.close()
  return zip_file

def zipfiles(files, use_genus, zip_out_fn=None, gformat=None, todisk=None):
  '''
  Write a zipfile from a list of files
  NOTE: Internal use only do not use as stand-alone! Will produce
  unexpected results.

  @param files: The filenames of the files to be zipped
  @type files: list

  @param use_genus: use the genus at the zipfile directory name
  @type use_genus: bool

  @param zip_out_fn: the output file name
  @type dir: string

  @param gformat: the format of the graphs being written out
  @type zip_file: string

  @param todisk: specify path if you want the zip written to disk as well
  @type todisk: string
  '''
  if zip_out_fn: # No filename provided for the zip archive
    print "Creating permanent file on disk %s ..." % zip_out_fn
    zip_file = zip_out_fn
    if not os.path.exists(zip_file):
      os.makedirs(os.path.dirname(zip_file))
  else:
    zip_file = tempfile.TemporaryFile(dir="/data/pytmp") # Don't close before done since auto delete

  zipf = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
  for fn in files:
    print "Compressing %s ..." % fn
    archive_name = fn if not use_genus else fn[fn.rfind(get_genus(fn)):]

    if isinstance(files, dict):
      archive_name = os.path.splitext(archive_name)[0]+"."+gformat
      fn = files[fn]

    zipf.write(os.path.abspath(fn), archive_name, zipfile.ZIP_DEFLATED)
  zipf.close()

  return zip_file

def unzip( zfilename, saveToDir ):
  '''
  Recursively unzip a zipped folder

  @param zfilename: full filename of the zipfile
  @type zfilename: string

  @param saveToDir: the save location
  @type saveToDir: string
  '''
  # open the zipped file
  zfile = zipfile.ZipFile(zfilename, "r", allowZip64=True)

  # get each archived file and process the decompressed data
  for info in zfile.infolist():
      fname = info.filename
      # decompress each file's data
      if os.path.splitext(fname)[1]:
          data = zfile.read(fname)

          # save the decompressed data to a new file
          filename = os.path.join(saveToDir, fname.split('/')[-1])
          fout = open(filename, "w")
          fout.write(data)
          fout.close()
          print "New file created --> %s" % filename
      else:
         print "Folder ignored --> %s" % fname

# Do not return file names here!

def main():
  parser = argparse.ArgumentParser(description='Zip the contents of an entire directory & place contents in single zip File')
  parser.add_argument('dirName', action='store')
  parser.add_argument('--multiTuple', action='store')

  result = parser.parse_args()

  zipFilesFromFolders(result.dirName, result.multiTuple)

if __name__ == '__main__':
  main()
