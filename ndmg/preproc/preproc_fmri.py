#!/usr/bin/env python

# Copyright 2016 NeuroData (http://neurodata.io)
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

# preproc_fmri.py
# Created by Eric Bridgeford on 2016-06-20-16.
# Email: ebridge2@jhu.edu

import numpy as np
import nibabel as nb
import sys
import os.path as op
import os.path
import nilearn as nl
from ndmg.utils import utils as mgu
from scipy import signal
from ndmg.stats import alignment_qc as mgqc


class preproc_fmri(object):

    def __init__(self):
        """
        Enables preprocessing of single images for single images. Has options
        to perform motion correction.
        """
        pass

    def motion_correct(self, mri, corrected_mri, idx):
        """
        Performs motion correction of a stack of 3D images.

        **Positional Arguments:**
            mri (String):
                 -the 4d (fMRI) image volume as a nifti file.
            corrected_mri (String):
                - the corrected and aligned fMRI image volume.
        """
        cmd = "mcflirt -in " + mri + " -out " + corrected_mri +\
            " -plots -refvol " + str(idx)
        mgu().execute_cmd(cmd)
        pass

    def slice_time_correct(self, mri, corrected_mri, stc=None):
        """
        Performs slice timing correction of a stack of 3D images.

        **Positional Arguments:**
            mri (String):
                 -the 4d (fMRI) image volume as a nifti file.
            corrected_mri (String):
                - the corrected and aligned fMRI image volume.
            stc: the slice timing correction options, a string
                  corresponding to the acquisition sequence.
                  Options are "/path/to/file", "down", "up",
                  "interleaved". If a file is passed, each line
                  should correspond to a single value (in TRs)
                  of the shift of each slice. For example,
                  if the first slice has no shift, the first line
                  in the text file would be "0.5".
                  If not None, make sure the "zooms" property is set
                  in your data (nb.load(mri).header.get_zooms()), otherwise
                  this function will throw an error.
        """
        if (stc is not None):
            cmd = "slicetimer -i " + mri + " -o " + corrected_mri
            if stc == "down":
                cmd += " --down"
            elif stc == "interleaved":
                cmd += " --odd"
            elif stc == "up":
                # do nothing, as this is default behavior
                pass
            elif op.isfile(stc):
                cmd += " --tcustom " + str(stc)
            else:
                raise ValueError("You have not passed a valid slice-timing " +
                                 "option")
            zooms = nb.load(mri).header.get_zooms()
            cmd += " -r " + str(zooms[3])
            mgu().execute_cmd(cmd)
        else:
            print "No slice timing information provided, so skipping."
        pass

    def smooth(self, mri, smoothed_mri):
        """
        Smooths a nifti image by applying a fwhm filter of specified diameter.

        *Positional Arguments:*
            mri: the mri to smooth.
            smoothed_mri: the smoothed mri path.
        """
        pass

    def preprocess(self, mri, preproc_mri, motion_mri,
                   outdir, stc=None, qcdir="", scanid=""):
        """
        A function to preprocess a stack of 3D images.

        **Positional Arguments:**

            mri:
                - the 4d (fMRI) image volume as a nifti file (String).
            motion_mri:
                - the 4d (fMRI) image volume that is motion aligned (String).
            preproc_mri:
                - the 4d (fMRI) preprocessed image volume
                as a nifti image (String).
            stc:
                - the slice timing correction information. See documentation
                  for slice_time_correct() for details.
            mri_name:
                - the name to append before all paths for file naming.
            outdir:
                - the location to place outputs (String).
            qcdir:
                - optional argument required for quality control output
                directory (String).
            scanid:
                - optional argument required for quality control, is the id
                of the subject (String).
        """
        mri_name = mgu().get_filename(mri)

        s0 = mgu().name_tmps(outdir, mri_name, "_0slice.nii.gz")
        stc_mri = mgu().name_tmps(outdir, mri_name, "_stc.nii.gz")
        # TODO EB: decide whether it is advantageous to align to mean image
        if (stc is not None):
            self.slice_time_correct(mri, stc_mri, stc)
        else:
            stc_mri = mri
        self.motion_correct(stc_mri, motion_mri, 0)

        if qcdir is not None:
            mgu().get_slice(motion_mri, 0, s0)
            mgqc().check_alignments(mri, motion_mri, s0, qcdir, mri_name,
                                    title="Motion Correction")
            mgqc().image_align(motion_mri, s0, qcdir, scanid=mri_name,
                               refid=mri_name + "_s0")

        cmd = "cp " + motion_mri + " " + preproc_mri
        mgu().execute_cmd(cmd)
        pass
