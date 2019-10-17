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
    d=tmp_path/"sub" 
    d.mkdir()
    temp_out = d / "test_out.nii.gz"
    out=  '../ndmg_outputs/tmp/reg_a/mni2t1w_warp.nii.gz'
    ref=  '../ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz'
    warp= '../ndmg_outputs/tmp/reg_a/warp_t12mni.nii.gz'
    inverse_warp(str(ref),str(temp_out), str(out))

    #load in the real image
    img1=nib.load(str(warp))
    Matrix_real=img1.get_fdata()
    img2=nib.load(str(temp_out))
    Matrix_output=img2.get_fdata()
    assert Matrix_output.all()==Matrix_real.all()



