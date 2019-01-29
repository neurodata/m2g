# !/usr/bin/env python

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

# gen_utils.py
# Created by Will Gray Roncal on 2016-01-28.
# Email: wgr@jhu.edu
# Edited by Eric Bridgeford.

from __future__ import print_function
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from subprocess import Popen, PIPE
import numpy as np
import nibabel as nb
import os.path as op
import sys
from networkx import to_numpy_matrix as graph2np
from ndmg.graph.zindex import XYZMorton
from scipy.sparse import lil_matrix

def execute_cmd(cmd, verb=False):
    """
    Given a bash command, it is executed and the response piped back to the
    calling script
    """
    if verb:
        print("Executing: {}".format(cmd))

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = p.communicate()
    code = p.returncode
    if code:
        sys.exit("Error {}: {}".format(code, err))
    return out, err


def name_tmps(basedir, basename, extension):
    return "{}/tmp/{}{}".format(basedir, basename, extension)

def get_b0(gtab, data):
    """
    Takes bval and bvec files and produces a structure in dipy format
    **Positional Arguments:**
    """
    b0 = np.where(gtab.b0s_mask)[0]
    b0_vol = np.squeeze(data[:, :, :, b0[0]])  # if more than 1, use first
    return b0_vol


def get_braindata(brain_file):
    """
    Opens a brain data series for a mask, mri image, or atlas.
    Returns a numpy.ndarray representation of a brain.
    **Positional Arguements**
        brain_file:
            - an object to open the data for a brain.
            Can be a string (path to a brain file),
            nibabel.nifti1.nifti1image, or a numpy.ndarray
    """
    if type(brain_file) is np.ndarray:  # if brain passed as matrix
        braindata = brain_file
    else:
        if type(brain_file) is str or type(brain_file) is unicode:
            brain = nb.load(str(brain_file))
        elif type(brain_file) is nb.nifti1.Nifti1Image:
            brain = brain_file
        else:
            raise TypeError("Brain file is type: {}".format(type(brain_file)) +
                            "; accepted types are numpy.ndarray, "
                            "string, and nibabel.nifti1.Nifti1Image.")
        braindata = brain.get_data()
    return braindata


def get_filename(label):
    """
    Given a fully qualified path gets just the file name, without extension
    """
    return op.splitext(op.splitext(op.basename(label))[0])[0]


def get_slice(mri, volid, sli):
    """
    Takes a volume index and constructs a new nifti image from
    the specified volume.
    **Positional Arguments:**
        mri:
            - the path to a 4d mri volume to extract a slice from.
        volid:
            - the index of the volume desired.
        sli:
            - the path to the destination for the slice.
    """
    mri_im = nb.load(mri)
    data = mri_im.get_data()
    # get the slice at the desired volume
    vol = np.squeeze(data[:, :, :, volid])

    # Wraps volume in new nifti image
    head = mri_im.get_header()
    head.set_data_shape(head.get_data_shape()[0:3])
    out = nb.Nifti1Image(vol, affine=mri_im.get_affine(),
                         header=head)
    out.update_header()
    # and saved to a new file
    nb.save(out, sli)


def make_gtab_and_bmask(fbval, fbvec, dwi_file, outdir):
    import nibabel as nib
    import os
    from nilearn.image import mean_img
    """
    Takes bval and bvec files and produces a structure in dipy format
    **Positional Arguments:**
    """
    # Use B0's from the DWI to create a more stable DWI image for registration
    nodif_B0 = "{}/nodif_B0.nii.gz".format(outdir)
    nodif_B0_mask = "{}/nodif_B0_mask.nii.gz".format(outdir)

    # loading bvecs/bvals
    print(fbval)
    print(fbvec)
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

    # Creating the gradient table
    gtab = gradient_table(bvals, bvecs)

    # Correct b0 threshold
    gtab.b0_threshold = min(bvals)

    # Get B0 indices
    B0s = np.where(gtab.bvals == gtab.b0_threshold)[0]
    print('B0\'s found at: ' + str(B0s))

    # Extract and Combine all B0s collected
    print('Extracting B0\'s...')
    cmds = []
    B0s_bbr = []
    for B0 in B0s:
        print(B0)
        B0_bbr = "{}/{}_B0.nii.gz".format(outdir, str(B0))
        cmd = 'fslroi ' + dwi_file + ' ' + B0_bbr + ' ' + str(B0) + ' 1'
        cmds.append(cmd)
        B0s_bbr.append(B0_bbr)

    for cmd in cmds:
        os.system(cmd)

    # Get mean B0
    mean_B0 = mean_img(B0s_bbr)
    nib.save(mean_B0, nodif_B0)

    # Get mean B0 brain mask
    cmd = 'fslmaths ' + nodif_B0 + ' -bin ' + nodif_B0_mask
    os.system(cmd)
    return gtab, nodif_B0_mask


def load_bval_bvec(fbval, fbvec):
    """
    Takes bval and bvec files and produces a structure in dipy format
    **Positional Arguments:**
    """
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    gtab = gradient_table(bvals, bvecs, atol=0.01)
    print(gtab.info)
    return gtab


def load_timeseries(timeseries_file, ts='roi'):
    """
    A function to load timeseries data. Exists to standardize
    formatting in case changes are made with how timeseries are
    saved in future versions.
     **Positional Arguments**
         timeseries_file: the file to load timeseries data from.
    """
    if (ts == 'roi') or (ts == 'voxel'):
        timeseries = np.load(timeseries_file)['roi']
        return timeseries
    else:
        print('You have not selected a valid timeseries type.' +
              'options are ts=\'roi\' or ts=\'voxel\'.')
    pass


def graph2mtx(graph):
    """
    A function to convert a networkx graph to an appropriate
    numpy matrix that is ordered properly from smallest
    ROI to largest.
    **Positional Arguments:**
        graph:
            - a networkx graph.
    """
    return graph2np(graph, nodelist=np.sort(graph.nodes()).tolist())


def name_tmps(basedir, basename, extension):
    return "{}/tmp/{}{}".format(basedir, basename, extension)


def morton_region(parcellation, outpath):
    """
    A function to compute which region each morton index is in.
    Col1 is the morton index. Col2 is the corresponding region
    the particular morton index falls into. 0 means it falls into
    a region unmapped in the parcellation.
    **Positional Arguments:**
        parcellation:
            - the input parcellation to compute over.
        outpath:
            - the filepath of the matrix.
    """
    at_dat = nb.load(parcellation).get_data()
    atlasn = get_filename(parcellation)
    dims = at_dat.shape
    region = {}
    for x in range(0, dims[0]):
        for y in range(0, dims[1]):
            for z in range(0, dims[2]):
                if at_dat[x, y, z] > 0:
                    region[XYZMorton((int(x), int(y), int(z)))] = at_dat[x, y, z]
    outf = op.join(outpath, atlasn + '_morton.csv')
    with open(outf, 'w')  as f:
        for key, val in region.iteritems():
            f.write('{},{}\n'.format(key, val))
        f.close()
    return


def parcel_overlap(parcellation1, parcellation2, outpath):
    """
    A function to compute the percent composition of each parcel in
    parcellation 1 with the parcels in parcellation 2. Rows are indices
    in parcellation 1; cols are parcels in parcellation 2. Values are the
    percent of voxels in parcel (parcellation 1) that fall into parcel
    (parcellation 2). Implied is that each row sums to 1.
    **Positional Arguments:**
        parcellation1:
            - the path to the first parcellation.
        parcellation2:
            - the path to the second parcellation.
        outpath:
            - the path to produce the output.
    """
    p1_dat = nb.load(parcellation1).get_data()
    p2_dat = nb.load(parcellation2).get_data()
    p1regs = np.unique(p1_dat)
    p1regs = p1regs[p1regs > 0]
    p2regs = np.unique(p2_dat)

    p1n = get_filename(parcellation1)
    p2n = get_filename(parcellation2)

    overlapdat = lil_matrix((p1regs.shape[0], p2regs.shape[0]), dtype=np.float32)
    for p1idx, p1reg in enumerate(p1regs):
        p1seq = (p1_dat == p1reg)
        N = p1seq.sum()
        poss_regs = np.unique(p2_dat[p1seq])
        for p2idx, p2reg in enumerate(p2regs):
            if (p2reg in poss_regs):
                # percent overlap is p1seq and'd with the anatomical region voxelspace, summed and normalized
                pover = np.logical_and(p1seq, p2_dat == p2reg).sum() / float(N)
                overlapdat[p1idx, p2idx] = pover

    outf = op.join(outpath, "{}_{}.csv".format(p1n, p2n))
    with open(outf, 'w')  as f:
        p2str = ["%s" % x for x in p2regs]
        f.write("p1reg," + ",".join(p2str) + "\n")
        for idx, p1reg in enumerate(p1regs):
            datstr = ["%.4f" % x for x in overlapdat[idx,].toarray()[0,]]
            f.write(str(p1reg) + "," + ",".join(datstr) + "\n")
        f.close()
    return
