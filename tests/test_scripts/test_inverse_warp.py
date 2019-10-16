"""This is the unit test of /ndmg/ndmg/utils/reg_utils.py/inverse_warp function"""
"""This function is used in ndmg/register/gen_reg.py/:def def t1w2dwi_align(self): mgru.inverse_warp() """
"""The t1w2dwi_align function is used in ndmg/scripts/ndmg_dwi_pipeline.py/reg.t1w2dwi_align(), which named ndmg_dwi_worker"""

import ndmg
from ndmg.utils import reg_utils as rgu
import nibabel as nib
import numpy as np
import pytest

def test_inverse_warp(tmp_path):
    #create temp directory to restore the out
    d=tmp_path/"sub"  
    d.mkdir()
    OUT_out_temp_path = d / "test_out.nii.gz"

    #out='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/mni2t1w_warp.nii.gz'
    #ref='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz'
    #warp='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/warp_t12mni.nii.gz'

    #set input/output data paths
    OUT_out_cntrl_path='../test_data/outputs/inverse_warp/mni2t1w_warp.nii.gz' #the real out
    ref_in_path='../test_data/inputs/inverse_warp/t1w_brain_nores.nii.gz' # the test input
    warp_in_path='../test_data/inputs/inverse_warp/warp_t12mni.nii.gz'    #the test input

    #load input data
    OUT_out_cntrl=nib.load(str(OUT_out_cntrl_path)).get_fdata()

    #call function
    rgu.inverse_warp(str(ref_in_path),str(OUT_out_temp_path), str(warp_in_path))  #calculating the test out
    
    #load function outputs
    OUT_out_temp=nib.load(str(OUT_out_temp_path)).get_fdata()
    
    #assert
    assert np.allclose(OUT_out_cntrl,OUT_out_temp)


