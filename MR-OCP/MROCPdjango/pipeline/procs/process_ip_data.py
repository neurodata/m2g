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

from ocpipeline.utils.util import sendJobCompleteEmail, sendJobFailureEmail
from ocpipeline.utils.filesorter import checkFileExtGengraph
from ocpipeline.procs.run_invariants import run_invariants
from ocpipeline.utils.util import getFiberID

from mrcap.gengraph import genGraph

# From the object
# 
def processInputData(session):
  '''
  Extract File name & determine what file corresponds to what for gengraph
  @param session: the session dictionary object
  '''
  if isinstance(session, str) or isinstance(session, unicode):
    f = open(session, "rb")
    session = pickle.load(f)
    f.close()

  filesInUploadDir = os.listdir(session['derivatives'])

  fiber_fn, data_atlas_fn = checkFileExtGengraph(filesInUploadDir) # Check & sort files

  ''' Fully qualify file names '''
  fiber_fn = os.path.join(session['derivatives'], fiber_fn)
  
  if not data_atlas_fn:
    data_atlas_fn = settings.ATLASES.keys()[0]
  else:
    data_atlas_fn = os.path.join(session['derivatives'], data_atlas_fn)

  print "data_atlas_fn %s ..." % data_atlas_fn

  Gfn = os.path.join(session['graphs'], getFiberID(fiber_fn)) # partial name
  if (session['graphsize']).lower().startswith("s"):
    Gfn += "smgr.graphml"
  elif (session['graphsize']).lower().startswith("b"):
    Gfn+="bggr.graphml"
  else: print '[ERROR]: Graphsize Unkwown' # should never happen
   
  try:
    session['Gfn']= genGraph(fiber_fn, data_atlas_fn, Gfn, session['graphsize'],\
                              numfibers=20000, **settings.ATLASES)
  except:
    msg = "Hello,\n\nYour most recent job failed either because your fiber streamline file or ROI mask was incorrectly formatted."
    msg += " Please check both and try again.%s\n\n" % (" "*randint(0,10))
    sendJobFailureEmail(session['email'], msg)

  # Run ivariants here
  if len(session['invariants']) > 0:
    print "Computing invariants ..."

    session['invariant_fns'] = run_invariants(session['invariants'],\
                                session['Gfn'], session['graphInvariants'])

  dwnldLoc = "http://mrbrain.cs.jhu.edu" + \
                  session['usrDefProjDir'].replace(' ','%20')
  sendJobCompleteEmail(session['email'], dwnldLoc)

def main():
  parser = argparse.ArgumentParser(description="")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()

if __name__ == "__main__":
  main()
