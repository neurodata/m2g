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

import warnings

warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op


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
                        mask[np.min((x[j] + 1, md[0] - 1)), y[j], z[j]] and
                        mask[x[j], np.min((y[j] + 1, md[1] - 1)), z[j]] and
                        mask[x[j], y[j], np.min((z[j] + 1, md[2] - 1))] and
                        mask[np.max((x[j] - 1, 0)), y[j], z[j]] and
                        mask[x[j], np.max((y[j] - 1, 0)), z[j]] and
                        mask[x[j], y[j], np.max((z[j] - 1, 0))]):
                    erode_mask[x[j], y[j], z[j]] = 1
        else:
            raise ValueError('Your mask erosion has an invalid shape.')
        mask = erode_mask
    return mask


def align_slices(dwi, corrected_dwi, idx):
    """
    Performs eddy-correction (or self-alignment) of a stack of 3D images
    **Positional Arguments:**
            dwi:
                - 4D (DTI) image volume as a nifti file
            corrected_dwi:
                - Corrected and aligned DTI volume in a nifti file
            idx:
                - Index of the first B0 volume in the stack
    """
    cmd = "eddy_correct {} {} {}".format(dwi, corrected_dwi, idx)
    status = mgu.execute_cmd(cmd, verb=True)


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
    prob = nib.load(prob_map)
    prob_dat = prob.get_data()
    mask = (prob_dat > t).astype(int)
    if erode > 0:
        mask = erode_mask(mask, v=erode)
    img = nib.Nifti1Image(mask,
                          header=prob.header,
                          affine=prob.get_affine())
    # save the corrected image
    nib.save(img, mask_path)
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
    # segment into CSF (pve_0), GM (pve_1), WM (pve_2)
    cmd = "fast -t 1 {} -n 3 -o {} {}".format(opts, basename, t1w)
    mgu.execute_cmd(cmd, verb=True)
    out = {}  # the outputs
    out['wm_prob'] = "{}_{}".format(basename, "pve_2.nii.gz")
    out['gm_prob'] = "{}_{}".format(basename, "pve_1.nii.gz")
    out['csf_prob'] = "{}_{}".format(basename, "pve_0.nii.gz")
    return out


def extract_brain(inp, out, opts=""):
    """
    A function to extract the brain from an image using FSL's BET.
    **Positional Arguments:**
        inp:
            - the input image.
        out:
            - the output brain extracted image.
    """
    print('extracting brain')
    cmd = "bet {} {} {}".format(inp, out, opts)
    os.system(cmd)

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
    cmd = "3dAutomask -dilate 2 -prefix {} {}".format(out, inp)
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
	- frac:
	    - fractional intensity threshold to apply.
    """
    cmd = "3dSkullStrip -prefix {} -input {}".format(out, t1w)
    mgu.execute_cmd(cmd, verb=True)
    pass


def extract_brain(inp, out, opts="-B"):
    """
    A function to extract the brain from an image using FSL's BET.
    **Positional Arguments:**
        inp:
            - the input image.
        out:
            - the output brain extracted image.
    """
    cmd = "bet {} {} {}".format(inp, out, opts)
    os.system(cmd)
    pass


def get_filename(label):
    """
    Given a fully qualified path gets just the file name, without extension
    """
    return op.splitext(op.splitext(op.basename(label))[0])[0]


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
    os.system(cmd)
    out = {}  # the outputs
    out['wm_prob'] = "{}_{}".format(basename, "pve_2.nii.gz")
    out['gm_prob'] = "{}_{}".format(basename, "pve_1.nii.gz")
    out['csf_prob'] = "{}_{}".format(basename, "pve_0.nii.gz")
    return out


def align(inp, ref, xfm=None, out=None, dof=12, searchrad=True,
          bins=256, interp=None, cost="mutualinfo", sch=None,
          wmseg=None, init=None, finesearch=None):
    """
    Aligns two images and stores the transform between them
    **Positional Arguments:**
            inp:
                - Input impage to be aligned as a nifti image file
            ref:
                - Image being aligned to as a nifti image file
            xfm:
                - Returned transform between two images
            out:
                - determines whether the image will be automatically
                aligned.
            dof:
                - the number of degrees of freedom of the alignment.
            searchrad:
                - a bool indicating whether to use the predefined
                searchradius parameter (180 degree sweep in x, y, and z).
            interp:
                - the interpolation method to use.
            sch:
                - the optional FLIRT schedule file.
            wmseg:
                - an optional white-matter segmentation for bbr.
            init:
                - an initial guess of an alignment.
    """
    cmd = "flirt -in {} -ref {}".format(inp, ref)
    if xfm is not None:
        cmd += " -omat {}".format(xfm)
    if out is not None:
        cmd += " -out {}".format(out)
    if dof is not None:
        cmd += " -dof {}".format(dof)
    if bins is not None:
        cmd += " -bins {}".format(bins)
    if interp is not None:
        cmd += " -interp {}".format(interp)
    if cost is not None:
        cmd += " -cost {}".format(cost)
    if searchrad is not None:
        cmd += " -searchrx -180 180 -searchry -180 180 " + \
               "-searchrz -180 180"
    if sch is not None:
        cmd += " -schedule {}".format(sch)
    if wmseg is not None:
        cmd += " -wmseg {}".format(wmseg)
    if init is not None:
        cmd += " -init {}".format(init)
    print(cmd)
    os.system(cmd)


def align_epi(epi, t1, brain, out):
    """
    Algins EPI images to T1w image
    """
    cmd = 'epi_reg --epi={} --t1={} --t1brain={} --out={}'
    cmd = cmd.format(epi, t1, brain, out)
    os.system(cmd)


def align_nonlinear(inp, ref, xfm, out, warp, ref_mask=None, in_mask=None, config=None):
    """
    Aligns two images using nonlinear methods and stores the
    transform between them.

    **Positional Arguments:**

        inp:
            - the input image.
        ref:
            - the reference image.
        affxfm:
            - the affine transform to use.
        warp:
            - the path to store the nonlinear warp.
        mask:
            - a mask in which voxels will be extracted
            during nonlinear alignment.
    """
    cmd = "fnirt --in={} --ref={} --aff={} --iout={} --cout={} --warpres=8,8,8"
    cmd = cmd.format(inp, ref, xfm, out, warp, config)
    if ref_mask is not None:
        cmd += " --refmask={} --applyrefmask=1".format(ref_mask)
    if in_mask is not None:
        cmd += " --inmask={} --applyinmask=1".format(in_mask)
    if config is not None:
        cmd += " --config={}".format(config)
    print(cmd)
    os.system(cmd)


def applyxfm(ref, inp, xfm, aligned, interp='trilinear', dof=6):
    """
    Aligns two images with a given transform

    **Positional Arguments:**

            inp:
                - Input impage to be aligned as a nifti image file
            ref:
                - Image being aligned to as a nifti image file
            xfm:
                - Transform between two images
            aligned:
                - Aligned output image as a nifti image file
    """
    cmd = "flirt -in {} -ref {} -out {} -init {} -interp {} -dof {} -applyxfm"
    cmd = cmd.format(inp, ref, aligned, xfm, interp, dof)
    print(cmd)
    os.system(cmd)


def apply_warp(ref, inp, out, warp, xfm=None, mask=None, interp=None, sup=False):
    """
    Applies a warp from the functional to reference space
    in a single step, using information about the structural->ref
    mapping as well as the functional to structural mapping.

    **Positional Arguments:**

        inp:
            - the input image to be aligned as a nifti image file.
        out:
            - the output aligned image.
        ref:
            - the image being aligned to.
        warp:
            - the warp from the structural to reference space.
        premat:
            - the affine transformation from functional to
            structural space.
    """
    cmd = "applywarp --ref=" + ref + " --in=" + inp + " --out=" + out + \
          " --warp=" + warp
    if xfm is not None:
        cmd += " --premat=" + xfm
    if mask is not None:
        cmd += " --mask=" + mask
    if interp is not None:
        cmd += " --interp=" + interp
    if sup is True:
        cmd += " --super --superlevel=a"
    print(cmd)
    os.system(cmd)


def inverse_warp(ref, out, warp):
    """
    Applies a warp from the functional to reference space
    in a single step, using information about the structural->ref
    mapping as well as the functional to structural mapping.

    **Positional Arguments:**

        inp:
            - the input image to be aligned as a nifti image file.
        out:
            - the output aligned image.
        ref:
            - the image being aligned to.
        warp:
            - the warp from the structural to reference space.
        premat:
            - the affine transformation from functional to
            structural space.
    """
    cmd = "invwarp --warp=" + warp + " --out=" + out + " --ref=" + ref
    print(cmd)
    os.system(cmd)


def resample(base, ingested, template):
    """
    Resamples the image such that images which have already been aligned
    in real coordinates also overlap in the image/voxel space.

    **Positional Arguments**
            base:
                - Image to be aligned
            ingested:
                - Name of image after alignment
            template:
                - Image that is the target of the alignment
    """
    # Loads images
    template_im = nib.load(template)
    base_im = nib.load(base)
    # Aligns images
    target_im = nl.resample_img(base_im,
                                target_affine=template_im.get_affine(),
                                target_shape=template_im.get_data().shape,
                                interpolation="nearest")
    # Saves new image
    nib.save(target_im, ingested)


def combine_xfms(xfm1, xfm2, xfmout):
    """
    A function to combine two transformations, and output the
    resulting transformation.

    **Positional Arguments**
        xfm1:
            - the path to the first transformation
        xfm2:
            - the path to the second transformation
        xfmout:
            - the path to the output transformation
    """
    cmd = "convert_xfm -omat {} -concat {} {}".format(xfmout, xfm1, xfm2)
    print(cmd)
    os.system(cmd)


def reslice_to_xmm(infile, vox_sz=2):
    cmd = "flirt -in {} -ref {} -out {} -nosearch -applyisoxfm {}"
    out_file = "%s%s%s%s%s%s" % (
        os.path.dirname(infile), '/', os.path.basename(infile).split('_pre_res')[0], '_res_', int(vox_sz), 'mm.nii.gz')
    cmd = cmd.format(infile, infile, out_file, vox_sz)
    os.system(cmd)
    return out_file
