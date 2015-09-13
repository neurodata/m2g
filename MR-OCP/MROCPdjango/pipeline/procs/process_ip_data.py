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

# process_ip_data.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse, os
import pickle

from django.conf import settings

from pipeline.utils.util import sendJobCompleteEmail, sendJobFailureEmail
from pipeline.utils.filesorter import checkFileExtGengraph
from pipeline.procs.run_invariants import run_invariants
from pipeline.utils.util import getFiberID, get_download_path

from mrcap.gengraph import genGraph

# From the object
def process_input_data(derivatives, graphs, graphsize, invariants, 
                        proj_dir, invariant_loc, to_email):
  '''
  Extract File name & determine what file corresponds to what for gengraph
  @param session: the session dictionary object
  '''
  """
  if isinstance(session, str) or isinstance(session, unicode):
    f = open(session, "rb")
    session = pickle.load(f)
    f.close()
  """

  filesInUploadDir = os.listdir(derivatives)

  fiber_fn, data_atlas_fn = checkFileExtGengraph(filesInUploadDir) # Check & sort files

  ''' Fully qualify file names '''
  fiber_fn = os.path.join(derivatives, fiber_fn)
  
  if not data_atlas_fn:
    data_atlas_fn = settings.ATLASES.keys()[0]
  else:
    data_atlas_fn = os.path.join(derivatives, data_atlas_fn)

  print "data_atlas_fn %s ..." % data_atlas_fn

  Gfn = os.path.join(graphs, getFiberID(fiber_fn)) # partial name
  if (graphsize).lower().startswith("s"):
    Gfn += "smgr.graphml"
    graphsize = False # False is small graph
  elif graphsize.lower().startswith("b"):
    Gfn+="bggr.graphml"
    graphsize = True # True is big graph
  else: print '[ERROR]: Graphsize Unkwown' # should never happen
   
  try:
    Gfn= genGraph(fiber_fn, data_atlas_fn, Gfn, graphsize, **settings.ATLASES) # numfibers = 20000 for tests
  except:
    msg = "Hello,\n\nYour most recent job failed either because your fiber streamline file or ROI mask was incorrectly formatted."
    msg += " Please check both and try again.\n\n"
    sendJobFailureEmail(to_email, msg)

  # Run ivariants here
  if len(invariants) > 0:
    print "Computing invariants ..."

    invariant_fns = run_invariants(invariants, Gfn, invariant_loc)

  dwnld_loc = get_download_path(proj_dir)
  sendJobCompleteEmail(to_email, dwnld_loc)
