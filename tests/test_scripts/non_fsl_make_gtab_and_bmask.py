import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock
import nibabel as nib
import dipy 
import dipy.external.fsl as dfsl
import numpy as np 
import pytest
import os

def make_gtab_and_bmask(fbval, fbvec, dwi_file, outdir):
    """Takes bval and bvec files and produces a structure in dipy format while also using FSL commands
    
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

    #temp adding mgu as import
    bvals, bvecs = mgu.read_bvals_bvecs(fbval, fbvec)

    # Creating the gradient table
    gtab = mgu.gradient_table(bvals, bvecs, atol=1.0)

    # Correct b0 threshold
    gtab.b0_threshold = min(bvals)

    # Get B0 indices
    B0s = np.where(gtab.bvals == gtab.b0_threshold)[0]
    print("%s%s" % ("B0's found at: ", B0s))

    # Show info
    print(gtab.info)

    # Extract and Combine all B0s collected
    print("Extracting B0's...")
    cmds = []
    B0s_bbr = []
    
    #load target image dwi_file
    dwi_file_loaded = nib.load(dwi_file)

    #Convert to numpy
    dwi_file_loaded_np =dwi_file_loaded.get_fdata()

    for B0 in B0s:
        print(B0)
        B0_bbr = "{}/{}_B0.nii.gz".format(outdir, str(B0))
        #save the B0th dimension, a 1 dimensional ROI at B0, the voxel corresponding to the B0th
        B0_dwi = dwi_file_loaded_np[:,:,:,B0]
        #convert back to nifti image using the affine of original image
        B0_nifti = nib.Nifti1Image(B0_dwi, dwi_file_loaded.affine)
        #save in path
        nib.save(B0_nifti, B0_bbr)

#old func
        # cmd = "fslroi " + dwi_file + " " + B0_bbr + " " + str(B0) + " 1"
        # cmds.append(cmd)

        B0s_bbr.append(B0_bbr)

    for cmd in cmds:
        print(cmd)
        os.system(cmd)

    # Get mean B0
    B0s_bbr_imgs = []
    for B0 in B0s_bbr:
        B0s_bbr_imgs.append(nib.load(B0))

    mean_B0 = mgu.mean_img(B0s_bbr_imgs)
    nib.save(mean_B0, nodif_B0)

# Get mean B0 brain mask
    # cmd = "bet " + nodif_B0 + " " + nodif_B0_bet + " -m -f 0.2"
    # os.system(cmd)

    #replace fsl bet through command line with dipy.external.fsl.bet 
    dfsl.bet(nodif_B0, nodif_B0_bet, options=' -m -f 0.2')

    return gtab, nodif_B0, nodif_B0_mask
