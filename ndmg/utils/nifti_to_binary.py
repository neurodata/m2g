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

# nifti_to_binary.py
# Created by Greg Kiar on 2016-07-05.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser

import os
import nibabel as nb
import numpy as np


def nib_to_bin(nii, dat):
    im = nb.load(nii)
    im_d = im.get_data()

    length = reduce(lambda x, y: x*y, im_d.shape)
    dat_d = np.reshape(im_d.astype(np.dtype('float32')), (1, length))
    with open(dat, 'wb') as fl:
        fl.write(dat_d)


def main():
    parser = ArgumentParser(description="")
    parser.add_argument("filenames", action="store", nargs="+", help="")
    result = parser.parse_args()

    niis = result.filenames
    dats = [os.path.splitext(os.path.splitext(fn)[0])[0]+'.dat' for fn in niis]

    for idx, fn in enumerate(niis):
        print "Converting: ", os.path.basename(fn)
        nib_to_bin(fn, dats[idx])
        print "Success!"


if __name__ == "__main__":
    main()
