
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
import os

from pipeline.utils.util import sendJobFailureEmail, sendJobCompleteEmail
from run_invariants import run_invariants
from pipeline.utils.util import get_download_path

def invariant_compute(invariants, graph_fn, invariants_path, data_dir, in_graph_format, to_email):
  """
  if isinstance(session, str) or isinstance(session, unicode):
    f = open(session, "rb")
    session = pickle.load(f)
    f.close()
  """
  dwnld_loc = get_download_path(data_dir)

  try:
    invariant_fns = run_invariants(invariants, graph_fn,
                invariants_path, 
                graph_format=in_graph_format)

    if isinstance(invariant_fns, str):
      raise Exception
    else:
      print 'Invariants for annoymous project %s complete...' % graph_fn

  except Exception, msg:
    msg = """
Hello,\n\nYour most recent job failed possibly because:\n- the graph '%s' you
uploaded does not match any accepted type.\n\n"You may have some partially
completed data here: %s.\nPlease check these and try again.\n\n
""" % (os.path.basename(graph_fn), dwnld_loc)

    sendJobFailureEmail(to_email, msg)
    return
  # Email user of job finished
  sendJobCompleteEmail(to_email, dwnld_loc)
