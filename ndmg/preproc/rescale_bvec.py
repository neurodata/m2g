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

# ndmg/preproc/rescale_bvec.py
# Created by Greg Kiar on 2016-02-12.
# Email: gkiar@jhu.edu

import numpy as np
import os.path as op


def rescale_bvec(bvec, bvec_new):
    """
    Normalizes b-vectors to be of unit length for the non-zero b-values. If the
    b-value is 0, the vector is untouched.

    Positional Arguments:
            - bvec:
                    File name of the original b-vectors file
            - bvec_new:
                    File name of the new (normalized) b-vectors file. Must have
                    extension `.bvec`
    """
    bv1 = np.array(np.loadtxt(bvec))
    # Enforce proper dimensions
    bv1 = bv1.T if bv1.shape[0] == 3 else bv1

    # Normalize values not close to norm 1
    bv2 = [b/np.linalg.norm(b) if not np.isclose(np.linalg.norm(b), 0)
           else b for b in bv1]

    try:
        assert(op.splitext(bvec_new)[1] == '.bvec')
        np.savetxt(bvec_new, bv2)
        pass
    except AssertionError:
        print 'Error: your new b-vector file must have extension .bvec to' +\
              ' be compatible with the the pipeline.'
        pass
    else:
        pass
    pass
