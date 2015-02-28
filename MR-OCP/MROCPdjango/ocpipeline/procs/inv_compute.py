
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

# asyn_inv_compute.py
# Created by Disa Mhembere on 2015-02-27.
# Email: disa@jhu.edu
# Copyright (c) 2015. All rights reserved.

import argparse
import pickle

from ocpipeline.utils.util import sendJobFailureEmail, sendJobCompleteEmail
from run_invariants import run_invariants

def invariant_compute(session):
  if isinstance(session, str) or isinstance(session, unicode):
    f = open(session, "rb")
    session = pickle.load(f)
    f.close()

  dwnldLoc = "http://mrbrain.cs.jhu.edu" + \
                      session['dataDir'].replace(' ','%20')
  for graph_fn in session['uploaded_graphs']:
    try:
      invariant_fns = run_invariants(session['invariants'], graph_fn,
                      session['graphInvariants'], 
                      graph_format=session['graph_format'])

      if isinstance(invariant_fns, str):
        raise Exception
      else:
        print 'Invariants for annoymous project %s complete...' % graph_fn

    except Exception, msg:
      msg = """
Hello,\n\nYour most recent job failed possibly because:\n- the graph '%s' you
uploaded does not match any accepted type.\n\n"You may have some partially
completed data here: %s.\nPlease check these and try again.\n\n
""" % (os.path.basename(graph_fn), dwnldLoc)

      sendJobFailureEmail(session['email'], msg)
      return

  # Email user of job finished
  sendJobCompleteEmail(session['email'], dwnldLoc)

def main():
  parser = argparse.ArgumentParser(description="Run invariants given ")
  parser.add_argument("ARG", action="", help="")
  parser.add_argument("-O", "--OPT", action="", help="")
  result = parser.parse_args()


if __name__ == "__main__":
  main()
