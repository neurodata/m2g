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

import os

from pipeline.utils.util import get_download_path
from pipeline.utils.util import sendJobCompleteEmail, sendJobFailureEmail, sendEmail
from computation.utils import convertTo

def convert(media_root, uploadedFiles, convert_file_save_loc, input_format, output_format, to_email):
  # Send begin job email
  content = "Hello,\n\n You requested the following files be converted:"
  for fn in uploadedFiles:
    content += "\n- " + os.path.basename(fn)
  content += "\n\nTo the following formats:"
  for fmt in output_format:
    content += "\n- " + fmt

  sendEmail(to_email, "Job launch Notification", content+"\n\n")
  # End Email junk

  err_msg = ""
  outfn = ""
  for fn in uploadedFiles:
    outfn, err_msg = convertTo.convert_graph(fn, input_format, convert_file_save_loc, *output_format)

  dwnld_loc = get_download_path(convert_file_save_loc)
  print "Download path: {0}".format(dwnld_loc)

  if (err_msg):
    err_msg = "Your job completed with errors. The result can be found at {}.\n\n"\
        "Message: %s\n\n" % err_msg
    sendJobFailureEmail(to_email, err_msg, dwnld_loc)
  else:
    sendJobCompleteEmail(to_email,dwnld_loc) 
