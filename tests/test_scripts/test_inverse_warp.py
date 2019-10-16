"""This is the unit test of /ndmg/ndmg/utils/reg_utils.py/inverse_warp function"""
"""This function is used in ndmg/register/gen_reg.py/:def def t1w2dwi_align(self): mgru.inverse_warp() """
"""The t1w2dwi_align function is used in ndmg/scripts/ndmg_dwi_pipeline.py/reg.t1w2dwi_align(), which named ndmg_dwi_worker"""

import nibabel as nib
import skimage.io as io
import numpy as np
import os
from ndmg.utils import reg_utils as rgu
from ndmg.utils.reg_utils import inverse_warp

def test_inverse_warp(tmp_path):
    #set up a temporary path to restore the out
    d=tmp_path/"sub"  
    d.mkdir()
    temp_out = d / "test_out.nii.gz"

    #out='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/mni2t1w_warp.nii.gz'
    #ref='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz'
    #warp='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/warp_t12mni.nii.gz'


    out='../test_data/outputs/mni2t1w_warp.nii.gz' #the real out
    ref='../test_data/inputs/t1w_brain_nores.nii.gz' # the test input
    warp='../test_data/inputs/warp_t12mni.nii.gz'    #the test input
    inverse_warp(str(ref),str(temp_out), str(warp))  #calculating the test out

    #load in the real out image
    img1=nib.load(str(out))
    Matrix_real_out=img1.get_fdata()
    #load in the test out image
    img2=nib.load(str(temp_out))
    Matrix_test_out=img2.get_fdata()
    #compare
    assert Matrix_real_out.all()==Matrix_test_out.all()


