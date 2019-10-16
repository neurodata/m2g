"""This is the unit test of /ndmg/ndmg/utils/reg_utils.py/applyxfm function"""
"""This function is used in the line949 of function dwi2atlas in gen_reg.py"""
"""The function dwi2atlas is used in line 508 of ndmg_dwi_pipeline.py"""

import nibabel as nib
import skimage.io as io
import numpy as np
import os
from ndmg.utils.reg_utils import applyxfm

def test_applyxfm(tmp_path):
    #set up a temporary path to restore the out
    d=tmp_path/"sub"  
    d.mkdir()
    temp_aligned = d / "test_aligned.nii.gz"

    #ref='/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    #inp='/Users/zhenhu/.ndmg/ndmg_atlases/atlases/mask/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-2x2x2_descr-brainmask.nii.gz'
    #xfm='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_m/roi_2_mni.mat'
    #aligned='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/vent_mask_mni.nii.gz'

    # the test input
    ref='../test_data/inputs/MNI152_T1_2mm_brain.nii.gz'
    inp='./test_data/inputs/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-2x2x2_descr-brainmask.nii.gz'
    xfm='./test_data/inputs/roi_2_mni.mat'
    aligned='../test_data/outputs/vent_mask_mni.nii.gz' #the real out

    applyxfm(ref, inp, xfm, str(temp_aligned), interp="trilinear", dof=6) #calculating the test out

    #load in the real out image
    img1=nib.load(str(aligned))
    Matrix_real_out=img1.get_fdata()
    #load in the test out image
    img2=nib.load(str(temp_aligned))
    Matrix_test_out=img2.get_fdata()
    #compare
    assert Matrix_real_out.all()==Matrix_test_out.all()
