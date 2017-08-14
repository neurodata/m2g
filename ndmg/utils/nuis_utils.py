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

# nuis_utils.py
# Created by Eric W Bridgeford on 2017-07-21.
# Email: ebridge2@jhu.edu

from ndmg.utils import utils as mgu
import nibabel as nb
import numpy as np


def erode_mask(mask, v=0):
    """
    A function to erode a mask by a specified number of
    voxels. Here, we define erosion as the process of checking
    whether all the voxels within a number of voxels for a
    mask have values.

    **Positional Arguments:**

        mask:
            - a numpy array of a mask to be eroded.
        v:
            - the number of voxels to erode by.
    """
    print("Eroding Mask...")
    for i in range(0, v):
        # masked_vox is a tuple 0f [x]. [y]. [z] cooords
        # wherever mask is nonzero
        erode_mask = np.zeros(mask.shape)
        x, y, z = np.where(mask != 0)
        if (x.shape == y.shape and y.shape == z.shape):
            # iterated over all the nonzero voxels
            for j in range(0, x.shape[0]):
                # check that the 3d voxels within 1 voxel are 1
                # if so, add to the new mask
                md = mask.shape
                if (mask[x[j], y[j], z[j]] and
                        mask[np.min((x[j]+1, md[0]-1)), y[j], z[j]] and
                        mask[x[j], np.min((y[j]+1, md[1]-1)), z[j]] and
                        mask[x[j], y[j], np.min((z[j]+1, md[2]-1))] and
                        mask[np.max((x[j]-1, 0)), y[j], z[j]] and
                        mask[x[j], np.max((y[j]-1, 0)), z[j]] and
                        mask[x[j], y[j], np.max((z[j]-1, 0))]):
                    erode_mask[x[j], y[j], z[j]] = 1
        else:
            raise ValueError('Your mask erosion has an invalid shape.')
        mask = erode_mask
    return mask


def probmap2mask(prob_map, mask_path, t, erode=0):
    """
    A function to extract a mask from a probability map.
    Also, performs mask erosion as a substep.

    **Positional Arguments:**

        prob_map:
            - the path to probability map for the given class
              of brain tissue.
        mask_path:
            - the path to the extracted mask.
        t:
            - the threshold to consider voxels part of the class.
        erode=0:
            - the number of voxels to erode by. Defaults to 0.
    """
    print("Extracting Mask from probability map {}...".format(prob_map))
    prob = nb.load(prob_map)
    prob_dat = prob.get_data()
    mask = (prob_dat > t).astype(int)
    if erode > 0:
        mask = erode_mask(mask, v=erode)
    img = nb.Nifti1Image(mask,
                         header=prob.header,
                         affine=prob.get_affine())
    # save the corrected image
    nb.save(img, mask_path)
    return mask_path


def segment_t1w(t1w, basename, opts=''):
    """
    A function to use FSL's FAST to segment an anatomical
    image into GM, WM, and CSF prob maps.

    **Positional Arguments:**

        t1w:
            - an anatomical T1w image.
        basename:
            - the basename for outputs. Often it will be
              most convenient for this to be the dataset,
              followed by the subject, followed by the step of
              processing. Note that this anticipates a path as well;
              ie, /path/to/dataset_sub_nuis, with no extension.
        opts:
            - additional options that can optionally be passed to
              fast. Desirable options might be -P, which will use
              prior probability maps if the input T1w MRI is in
              standard space.
    """
    print("Segmenting Anatomical Image into WM, GM, and CSF...")
    # run FAST, with options -t for the image type and -n to
    # segment into CSF (pve_0), WM (pve_1), GM (pve_2)
    cmd = "fast -t 1 {} -n 3 -o {} {}".format(opts, basename, t1w)
    mgu.execute_cmd(cmd, verb=True)
    out = {}  # the outputs
    out['wm_prob'] = "{}_{}".format(basename, "pve_2.nii.gz")
    out['gm_prob'] = "{}_{}".format(basename, "pve_1.nii.gz")
    out['csf_prob'] = "{}_{}".format(basename, "pve_0.nii.gz")
    return out
