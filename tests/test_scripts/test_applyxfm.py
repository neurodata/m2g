"""This is the unit test of /ndmg/ndmg/utils/reg_utils.py/applyxfm function"""
"""This function is used in the line949 of function dwi2atlas in gen_reg.py"""
"""The function dwi2atlas is used in line 508 of ndmg_dwi_pipeline.py"""

import ndmg
from ndmg.utils import reg_utils as rgu
import nibabel as nib
import numpy as np


def test_applyxfm(tmp_path):
    #set up a temporary path to restore the aligned
    d=tmp_path/"sub"  
    d.mkdir()
    aligned_out_temp_path = d / "test_aligned.nii.gz"

    #ref='/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
    #inp='/Users/zhenhu/.ndmg/ndmg_atlases/atlases/mask/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-2x2x2_descr-brainmask.nii.gz'
    #xfm='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_m/roi_2_mni.mat'
    #aligned='/Users/zhenhu/Documents/Neuro_Data_Design/Downloads/ndmg_outputs/tmp/reg_a/vent_mask_mni.nii.gz'

    # the test input
    ref_in_path='../test_data/inputs/applyxfm/MNI152_T1_2mm_brain.nii.gz'
    inp_in_path='../test_data/inputs/applyxfm/HarvardOxford-thr25_space-MNI152NLin6_variant-lateral-ventricles_res-2x2x2_descr-brainmask.nii.gz'
    xfm_in_path='../test_data/inputs/applyxfm/roi_2_mni.mat'

    aligned_out_cntrl_path='../test_data/outputs/applyxfm/vent_mask_mni.nii.gz' #the real out

    #load input data
    aligned_out_cntrl=nib.load(str(aligned_out_cntrl_path)).get_fdata()

    #call function
    rgu.applyxfm(str(ref_in_path),str(inp_in_path),str(xfm_in_path),str(aligned_out_temp_path)) 
    
    #load function outputs
    aligned_out_temp=nib.load(str(aligned_out_temp_path)).get_fdata()
    
    #assert
    assert np.allclose(aligned_out_cntrl,aligned_out_temp)