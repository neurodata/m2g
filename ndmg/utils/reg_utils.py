# Copyright 2017 NeuroData (http://neurodata.io)
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

# reg_utils.py
# Created by Eric Bridgeford on 2017-06-21.
# Email: ebridge2@jhu.edu

from ndmg.utils import utils as mgu


def apply_mask(inp, mask, out):
    """
    A function to generate a brain-only mask for an input image.

    **Positional Arguments:**

        - inp:
            - the input image. If 4d, the mask should be 4d. If 3d, the
              mask should be 3d.
        - mask:
            - the mask to apply to the data. Should be nonzero in mask region.
        - out:
            - the path to the skull-extracted image.
    """
    cmd = "3dcalc -a {} -b {} -expr 'a*step(b)' -prefix {}"
    cmd = cmd.format(inp, mask, out)
    mgu.execute_cmd(cmd, verb=True)
    pass


def extract_epi_brain(epi, out, tmpdir):
    """
    A function to extract the brain from an input 4d EPI image
    using AFNI's brain extraction utilities.

    **Positional Arguments:**

        - epi:
            - the path to a 4D epi image.
        - out:
            - the path to the EPI brain.
        - tmpdir:
            - the directory to place temporary files.
    """
    epi_name = mgu.get_filename(epi)
    epi_mask = "{}/{}_mask.nii.gz".format(tmpdir, epi_name)
    # 3d automask to extract the mask itself from the 4d data
    extract_mask(epi, epi_mask)
    # 3d calc to apply the mask to the 4d image
    apply_mask(epi, epi_mask, out)
    pass


def extract_mask(inp, out):
    """
    A function that extracts a mask from images using AFNI's
    3dAutomask algorithm.

    **Positional Arguments:**

        - inp:
            the input image. Can be a skull-stripped T1w (from 3dSkullStrip)
            or a 4d EPI image.
        - out:
            - the path to the extracted mask.
    """
    cmd = "3dAutomask -prefix {} {}".format(out, inp)
    mgu.execute_cmd(cmd, verb=True)
    pass


def extract_t1w_brain(t1w, out, tmpdir):
    """
    A function to extract the brain from an input T1w image
    using AFNI's brain extraction utilities.

    **Positional Arguments:**

        - t1w:
            - the input T1w image.
        - out:
            - the output T1w brain.
        - tmpdir:
            - the temporary directory to store images.
    """
    t1w_name = mgu.get_filename(t1w)
    # the t1w image with the skull removed.
    skull_t1w = "{}/{}_noskull.nii.gz".format(tmpdir, t1w_name)
    # 3dskullstrip to extract the brain-only t1w
    t1w_skullstrip(t1w, skull_t1w)
    # 3dcalc to apply the mask over the 4d image
    apply_mask(t1w, skull_t1w, out)
    pass


def normalize_t1w(inp, out):
    """
    A function that normalizes intensity values for anatomical
    T1w images. Makes brain extraction much more robust
    in the event that we have poor shading in our T1w image.

    **Positional Arguments:**

        - inp:
            - the input T1w image.
        - out:
            - the output intensity-normalized image.
    """
    cmd = "3dUnifize -prefix {} -input {}".format(out, inp)
    mgu.execute_cmd(cmd, verb=True)
    pass


def resample_fsl(base, res, goal_res, interp='spline'):
    """
    A function to resample a base image in fsl to that of a template.

    **Positional Arguments:**

        base:
            - the path to the base image to resample.
        res:
            - the filename after resampling.
        goal_res:
            - the desired resolution.
        interp:
            - the interpolation strategy to use.
    """
    # resample using an isometric transform in fsl
    cmd = "flirt -in {} -ref {} -out {} -applyisoxfm {} -interp {}"
    cmd = cmd.format(base, base, res, goal_res, interp)
    mgu.execute_cmd(cmd, verb=True)
    pass


def t1w_skullstrip(t1w, out):
    """
    A function that skull-strips T1w images using AFNI's 3dSkullStrip
    algorithm, which is a modification of FSL's BET specialized to T1w
    images. This offers robust skull-stripping with no hyperparameters.
    Note that this function renormalizes the intensities, so make sure
    to call extract_t1w_brain if the goal is to retrieve the original
    intensity values.

    **Positional Arguments:**

        - inp:
            - the input T1w image.
        - out:
            - the output skull-stripped image.
    """
    cmd = "3dSkullStrip -prefix {} -input {}".format(out, t1w)
    mgu.execute_cmd(cmd, verb=True)
    pass
