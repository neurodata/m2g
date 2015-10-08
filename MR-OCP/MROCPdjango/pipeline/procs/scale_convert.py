
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

#!/usr/bin/env python

# scale_convert.py
# Created by Disa Mhembere on 2015-03-15.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import tempfile
import os

from pipeline.utils.zipper import zipfiles
from pipeline.utils.util import get_genus
from mrcap.utils.downsample import downsample
from mrcap.utils import igraph_io
from pipeline.utils.util import sendJobFailureEmail, sendJobCompleteEmail

def scale_convert(selected_files, dl_format, ds_factor, ATLASES, email=None, dwnld_loc=None, zip_fn=None):
  # Debug
  print "Entering scale function ..."
  try:
    if dl_format == "graphml" and ds_factor == 0:
      temp = zipfiles(selected_files, use_genus=True, zip_out_fn=zip_fn)

    else:
      files_to_zip = {}

      for fn in selected_files:
        # No matter what we need a temp file
        print "Creating temp file ..."
        tmpfile = tempfile.NamedTemporaryFile("w", delete=False, dir="/data/pytmp")
        print "Temp file %s created ..." % tmpfile.name
        tmpfile.close()

        # Downsample only valid for *BIG* human brains!
        # *NOTE: If smallgraphs are ingested this will break

        if ds_factor and get_genus(fn) == "human":
          if isinstance(ds_factor, int):
            print "downsampling to factor %d" % ds_factor
            g = downsample(igraph_io.read_arbitrary(fn, "graphml"), ds_factor)
            print "downsample complete"
          else:
            g = downsample(igraph_io.read_arbitrary(fn, "graphml"), atlas=nib_load(ATLASES[ds_factor]))
        else:
          g = igraph_io.read_arbitrary(fn, "graphml")

        # Write to `some` format
        if dl_format == "mm":
          igraph_io.write_mm(g, tmpfile.name)
        else:
          g.write(tmpfile.name, format=dl_format)

        files_to_zip[fn] = tmpfile.name

      temp = zipfiles(files_to_zip, use_genus=True, zip_out_fn=zip_fn, gformat=dl_format)
      # Del temp files
      for tmpfn in files_to_zip.values():
        print "Deleting %s ..." % tmpfn
        os.remove(tmpfn)

  except Exception, msg:
    print "An exception was thrown and caught with message %s!" % msg
    if email:
      msg = """
Hello,\n\nYour most recent job failed to complete.
\nYou may have some partially completed data at {}.\n\n
"""
      sendJobFailureEmail(email, msg, dwnld_loc)
      return
    else:
      return 'An error occurred while processing your request. Please send an email to \
              <a href="mailto:jhmrocp@cs.jhu.edu">jhmrocp@cs.jhu.edu</a> with the details of your request.'

  if email:
    # Email user of job finished
    sendJobCompleteEmail(email, dwnld_loc)
    return

  return temp # Case where its an iteractive download
