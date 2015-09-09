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

# convert.py
# Created by Disa Mhembere on 2015-03-16.
# Email: disa@jhu.edu

import argparse
import os
from time import strftime, localtime
from glob import glob

from pipeline.utils.util import saveFileToDisk
from pipeline.utils.util import sendJobCompleteEmail, sendJobFailureEmail, sendEmail
from computation.utils import convertTo

def convert(media_root, upload_fn, upload, input_format, output_format, to_email):
  baseDir = os.path.join(media_root, 'tmp', strftime('formUpload%a%d%b%Y_%H.%M.%S/', localtime()))
  saveDir = os.path.join(baseDir,'upload') # Save location of original uploads
  convertFileSaveLoc = os.path.join(baseDir,'converted') # Save location of converted data

  if not (os.path.exists(convertFileSaveLoc)):
    os.makedirs(convertFileSaveLoc)

  savedFile = os.path.join(saveDir, upload_fn)

  saveFileToDisk(upload, savedFile)

  # If zip is uploaded
  if os.path.splitext(upload_fn)[1].strip() == '.zip':
    unzip(savedFile, saveDir)
    # Delete zip so its not included in the graphs we uploaded
    os.remove(savedFile)
    uploadedFiles = glob(os.path.join(saveDir, "*")) # get the uploaded file names

  else:
    uploadedFiles = [savedFile]

  # Send begin job email
  content = "Hello,\n\n You requested the following files be converted:"
  for fn in uploadedFiles:
    content += "\n- " + os.path.basename(fn)
  content += "\n\nTo the following formats:"
  for fmt in output_format:
    content += "\n- " + fmt

  #content += "\n\nThanks for using MROCP,\nThe MROCP team"

  sendEmail(to_email, "Job launch Notification", content+"\n\n")
  # End Email junk

  err_msg = ""
  outfn = ""
  for fn in uploadedFiles:
    outfn, err_msg = convertTo.convert_graph(fn, input_format, convertFileSaveLoc, *output_format)

  dwnldLoc = "http://mrbrain.cs.jhu.edu" + convertFileSaveLoc.replace(' ','%20')
  
  if (err_msg):
    err_msg = "Your job completed with errors. The result can be found <a href=\"%s\" target=\"blank\">here</a>.<br> Message %s" % (dwnldLoc, err_msg)
    sendJobFailureEmail(to_email, err_msg)
  else:
    sendJobCompleteEmail(to_email,dwnldLoc) 

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()

if __name__ == "__main__":
  main()
