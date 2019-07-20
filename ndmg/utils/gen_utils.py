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

import warnings
warnings.simplefilter("ignore")
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from subprocess import Popen, PIPE
import numpy as np
import nibabel as nib
import os
import os.path as op
import sys
import shutil
import pyximport
from nilearn.image import mean_img

try:
    from ndmg.graph.zindex import XYZMorton
except:
    pyximport.install()
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
        if type(brain_file) is str or type(brain_file) is str:
            brain = nib.load(str(brain_file))
        elif type(brain_file) is nib.nifti1.Nifti1Image:
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
    mri_im = nib.load(mri)
    data = mri_im.get_data()
    # get the slice at the desired volume
    vol = np.squeeze(data[:, :, :, volid])

    # Wraps volume in new nifti image
    head = mri_im.get_header()
    head.set_data_shape(head.get_data_shape()[0:3])
    out = nib.Nifti1Image(vol, affine=mri_im.get_affine(),
                          header=head)
    out.update_header()
    # and saved to a new file
    nib.save(out, sli)


def make_gtab_and_bmask(fbval, fbvec, dwi_file, outdir):
    """Takes bval and bvec files and produces a structure in dipy format
    
    Parameters
    ----------
    fbval : str
        b-value file
    fbvec : str
        b-vector file
    dwi_file : str
        dwi file being analyzed
    outdir : str
        output directory
    
    Returns
    -------
    GradientTable
        gradient table created from bval and bvec files
    str
        location of averaged b0 image file
    str
        location of b0 brain mask file
    """
    
    # Use B0's from the DWI to create a more stable DWI image for registration
    nodif_B0 = "{}/nodif_B0.nii.gz".format(outdir)
    nodif_B0_bet = "{}/nodif_B0_bet.nii.gz".format(outdir)
    nodif_B0_mask = "{}/nodif_B0_bet_mask.nii.gz".format(outdir)

    # loading bvecs/bvals
    print(fbval)
    print(fbvec)
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)

    # Creating the gradient table
    gtab = gradient_table(bvals, bvecs, atol=1.0)

    # Correct b0 threshold
    gtab.b0_threshold = min(bvals)

    # Get B0 indices
    B0s = np.where(gtab.bvals == gtab.b0_threshold)[0]
    print("%s%s" % ('B0\'s found at: ', B0s))

    # Show info
    print(gtab.info)

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
        print(cmd)
        os.system(cmd)

    # Get mean B0
    B0s_bbr_imgs = []
    for B0 in B0s_bbr:
        B0s_bbr_imgs.append(nib.load(B0))

    mean_B0 = mean_img(B0s_bbr_imgs)
    nib.save(mean_B0, nodif_B0)

    # Get mean B0 brain mask
    cmd = 'bet ' + nodif_B0 + ' ' + nodif_B0_bet + ' -m -f 0.2'
    os.system(cmd)
    return gtab, nodif_B0, nodif_B0_mask


def reorient_dwi(dwi_prep, bvecs, namer):
    """Orients dwi data to the proper orientation (RADIOLOGICAL) through Posterior-Anterior and Inferior-Superior flipping
    
    Parameters
    ----------
    dwi_prep : str
        Location of eddy corrected dwi file
    bvecs : str
        Location of the resaled b-vector file
    namer : name_resource
        name_resource variable containing relevant directory tree information
    
    Returns
    -------
    str
        location of potentially reoriented eddy corrected dwi file
    str
        location of potentially reoriented b-vector file
    """
    import shutil
    # Check orientation (dwi_prep) by getting the orientation contained in the dwi file
    cmd = 'fslorient -getorient ' + dwi_prep
    cmd_run = os.popen(cmd)
    orient = cmd_run.read().strip('\n')
    cmd_run.close()
    dwi_orig = dwi_prep
    dwi_prep = "{}/{}_pre_reor.nii.gz".format(namer.dirs['output']['prep_dwi'],
                                              dwi_prep.split('/')[-1].split('.nii.gz')[0])
    shutil.copyfile(dwi_orig, dwi_prep)
    bvecs_orig = bvecs
    bvecs = "{}/bvecs.bvec".format(namer.dirs['output']['prep_dwi'])
    shutil.copyfile(bvecs_orig, bvecs)
    bvecs_mat = np.genfromtxt(bvecs)
    cmd = 'fslorient -getqform ' + dwi_prep
    cmd_run = os.popen(cmd)
    qform = cmd_run.read().strip('\n')
    cmd_run.close()
    reoriented = False
    if orient == 'NEUROLOGICAL':
        reoriented = True
        print('Neurological (dwi), reorienting to radiological...')
        # Orient dwi to RADIOLOGICAL
        # Posterior-Anterior Reorientation
        if float(qform.split(' ')[:-1][5]) <= 0:
            dwi_prep_PA = "{}/dwi_reor_PA.nii.gz".format(namer.dirs['output']['prep_dwi'])
            print('Reorienting P-A flip (dwi)...')
            cmd = 'fslswapdim ' + dwi_prep + ' -x -y z ' + dwi_prep_PA
            os.system(cmd)
            bvecs_mat[:,1] = -bvecs_mat[:,1]
            cmd = 'fslorient -getqform ' + dwi_prep_PA
            cmd_run = os.popen(cmd)
            qform = cmd_run.read().strip('\n')
            cmd_run.close()
            dwi_prep = dwi_prep_PA
        # Inferior-Superior Reorientation
        if float(qform.split(' ')[:-1][10]) <= 0:
            dwi_prep_IS = "{}/dwi_reor_IS.nii.gz".format(namer.dirs['output']['prep_dwi'])
            print('Reorienting I-S flip (dwi)...')
            cmd = 'fslswapdim ' + dwi_prep + ' -x y -z ' + dwi_prep_IS
            os.system(cmd)
            bvecs_mat[:,2] = -bvecs_mat[:,2]
            dwi_prep = dwi_prep_IS
        bvecs_mat[:, 0] = -bvecs_mat[:, 0]
        cmd = 'fslorient -forceradiological ' + dwi_prep
        os.system(cmd)
        np.savetxt(bvecs, bvecs_mat)
    else:
        print('Radiological (dwi)...')
        # Posterior-Anterior Reorientation
        if float(qform.split(' ')[:-1][5]) <= 0:
            dwi_prep_PA = "{}/dwi_reor_PA.nii.gz".format(namer.dirs['output']['prep_dwi'])
            print('Reorienting P-A flip (dwi)...')
            cmd = 'fslswapdim ' + dwi_prep + ' -x -y z ' + dwi_prep_PA
            os.system(cmd)
            bvecs_mat[:,1] = -bvecs_mat[:,1]
            cmd = 'fslorient -getqform ' + dwi_prep_PA
            cmd_run = os.popen(cmd)
            qform = cmd_run.read().strip('\n')
            cmd_run.close()
            dwi_prep = dwi_prep_PA
            reoriented = True
        # Inferior-Superior Reorientation
        if float(qform.split(' ')[:-1][10]) <= 0:
            dwi_prep_IS = "{}/dwi_reor_IS.nii.gz".format(namer.dirs['output']['prep_dwi'])
            print('Reorienting I-S flip (dwi)...')
            cmd = 'fslswapdim ' + dwi_prep + ' -x y -z ' + dwi_prep_IS
            os.system(cmd)
            bvecs_mat[:,2] = -bvecs_mat[:,2]
            dwi_prep = dwi_prep_IS
            reoriented = True
        np.savetxt(bvecs, bvecs_mat)

    if reoriented is True:
        imgg = nib.load(dwi_prep)
        data = imgg.get_fdata()
        affine = imgg.affine
        hdr = imgg.header
        imgg = nib.Nifti1Image(data, affine=affine, header=hdr)
        imgg.set_sform(affine)
        imgg.set_qform(affine)
        imgg.update_header()
        nib.save(imgg, dwi_prep)

        print('Reoriented affine: ')
        print(affine)
    else:
        dwi_prep = dwi_orig
        print('Image already in RAS+')

    return dwi_prep, bvecs


def reorient_t1w(t1w, namer):
    """Orients t1w data to the proper orientation (RADIOLOGICAL) through Posterior-Anterior and Inferior-Superior flipping
    
    Parameters
    ----------
    t1w : str
        Location of t1w file
    namer : name_resource
        name_resource variable containing relevant directory tree information
    
    Returns
    -------
    str
        location of reoriented t1w file
    """
    import shutil
    import random
    cmd = 'fslorient -getorient ' + t1w
    cmd_run = os.popen(cmd)
    orient = cmd_run.read().strip('\n')
    cmd_run.close()
    t1w_orig = t1w
    hash = str(random.randint(1, 10000))
    t1w = "{}/{}_pre_reor_{}.nii.gz".format(namer.dirs['output']['prep_anat'],
                                            t1w.split('/')[-1].split('.nii.gz')[0], hash)
    shutil.copyfile(t1w_orig, t1w)
    cmd = 'fslorient -getqform ' + t1w
    cmd_run = os.popen(cmd)
    qform = cmd_run.read().strip('\n')
    cmd_run.close()
    reoriented = False
    if orient == 'NEUROLOGICAL':
        reoriented = True
        print('Neurological (t1w), reorienting to radiological...')
        # Orient t1w to std
        # Posterior-Anterior Reorientation
        if float(qform.split(' ')[:-1][5]) <= 0:
            t1w_PA = "{}/t1w_reor_PA.nii.gz".format(namer.dirs['output']['prep_anat'])
            print('Reorienting P-A flip (t1w)...')
            cmd = 'fslswapdim ' + t1w + ' -x -y z ' + t1w_PA
            os.system(cmd)
            cmd = 'fslorient -getqform ' + t1w_PA
            cmd_run = os.popen(cmd)
            qform = cmd_run.read().strip('\n')
            cmd_run.close()
            t1w = t1w_PA
        # Inferior-Superior Reorientation
        if float(qform.split(' ')[:-1][10]) <= 0:
            t1w_IS = "{}/t1w_reor_IS.nii.gz".format(namer.dirs['output']['prep_anat'])
            print('Reorienting I-S flip (t1w)...')
            cmd = 'fslswapdim ' + t1w + ' -x y -z ' + t1w_IS
            os.system(cmd)
            t1w = t1w_IS
        cmd = 'fslorient -forceradiological ' + t1w
        os.system(cmd)
    else:
        print('Radiological (t1w)...')
        # Posterior-Anterior Reorientation
        if float(qform.split(' ')[:-1][5]) <= 0:
            t1w_PA = "{}/t1w_reor_PA.nii.gz".format(namer.dirs['output']['prep_anat'])
            print('Reorienting P-A flip (t1w)...')
            cmd = 'fslswapdim ' + t1w + ' -x -y z ' + t1w_PA
            os.system(cmd)
            cmd = 'fslorient -getqform ' + t1w_PA
            cmd_run = os.popen(cmd)
            qform = cmd_run.read().strip('\n')
            cmd_run.close()
            t1w = t1w_PA
            reoriented = True
        # Inferior-Superior Reorientation
        if float(qform.split(' ')[:-1][10]) <= 0:
            t1w_IS = "{}/t1w_reor_IS.nii.gz".format(namer.dirs['output']['prep_anat'])
            print('Reorienting I-S flip (t1w)...')
            cmd = 'fslswapdim ' + t1w + ' -x y -z ' + t1w_IS
            os.system(cmd)
            t1w = t1w_IS
            reoriented = True

    if reoriented is True:
        imgg = nib.load(t1w)
        data = imgg.get_fdata()
        affine = imgg.affine
        hdr = imgg.header
        imgg = nib.Nifti1Image(data, affine=affine, header=hdr)
        imgg.set_sform(affine)
        imgg.set_qform(affine)
        imgg.update_header()
        nib.save(imgg, t1w)

        print('Reoriented affine: ')
        print(affine)
    else:
        t1w = t1w_orig
        print('Image already in RAS+')

    return t1w


def match_target_vox_res(img_file, vox_size, namer, sens):
    """Reslices input MRI file if it does not match the targeted voxel resolution. Can take dwi or t1w scans.
    
    Parameters
    ----------
    img_file : str
        location of file to be resliced
    vox_size : str
        target voxel resolution ('2mm' or '1mm')
    namer : name_resource
        name_resource variable containing relevant directory tree information
    sens : str
        type of data being analyzed ('dwi' or 'func')
    
    Returns
    -------
    str
        location of potentially resliced image
    """
    from dipy.align.reslice import reslice
    # Check dimensions
    img = nib.load(img_file)
    data = img.get_fdata()
    affine = img.affine
    hdr = img.header
    zooms = hdr.get_zooms()[:3]
    if vox_size == '1mm':
        new_zooms = (1., 1., 1.)
    elif vox_size == '2mm':
        new_zooms = (2., 2., 2.)

    if (abs(zooms[0]), abs(zooms[1]), abs(zooms[2])) != new_zooms:
        print('Reslicing image ' + img_file + ' to ' + vox_size + '...')
        if sens == 'dwi':
            img_file_pre = "{}/{}_pre_res.nii.gz".format(namer.dirs['output']['prep_dwi'],
                                                         os.path.basename(img_file).split('.nii.gz')[0])
            shutil.copyfile(img_file, img_file_pre)
        elif sens == 't1w':
            img_file_pre = "{}/{}_pre_res.nii.gz".format(namer.dirs['output']['prep_anat'],
                                                         os.path.basename(img_file).split('.nii.gz')[0])
            shutil.copyfile(img_file, img_file_pre)
        data2, affine2 = reslice(data, affine, zooms, new_zooms)
        if sens == 'dwi':
            affine2[0:3, 3] = np.zeros(3)
            affine2[0:3, 0:3] = np.eye(3) * np.array(new_zooms) * np.sign(affine2[0:3, 0:3])
        img2 = nib.Nifti1Image(data2, affine=affine2, header=hdr)
        img2.set_qform(affine2)
        img2.set_sform(affine2)
        img2.update_header()
        nib.save(img2, img_file)
        print('Resliced affine: ')
        print(nib.load(img_file).affine)
    else:
        if sens == 'dwi':
            affine[0:3,3] = np.zeros(3)
        img = nib.Nifti1Image(data, affine=affine, header=hdr)
        img.set_sform(affine)
        img.set_qform(affine)
        img.update_header()
        nib.save(img, img_file)

    return img_file


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
    at_dat = nib.load(parcellation).get_data()
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
        for key, val in region.items():
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
    p1_dat = nib.load(parcellation1).get_data()
    p2_dat = nib.load(parcellation2).get_data()
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
