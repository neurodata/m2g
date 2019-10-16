import warnings
warnings.simplefilter("ignore")
import ndmg
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgr
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op
import pytest

def test_align(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    omat_out_temp_path = d / "omat.data"
    outnii_out_temp_path = d / "outnii.nii.gz"
    
    # set input/ouput data paths
    align_in_path = r"../test_data/inputs/align/sub-0025864_ses-1_T1w.nii.gz"
    ref_in_path = r"../test_data/inputs/align/MNI152_T1_2mm_brain.nii.gz"
    outnii_out_cntrl_path = r"../test_data/outputs/align/outnii.nii.gz"
    
    # call function
    inp = align_in_path
    ref = ref_in_path
    xfm = omat_out_temp_path
    out = outnii_out_temp_path
    mgr.align(inp, ref, xfm, out)
    
    # load function outputs
    outnii_out_temp = nib.load(str(out)).get_fdata()
    
    # load output data
    outnii_out_cntrl = nib.load(str(outnii_out_cntrl_path)).get_fdata()
    
    # assert
    assert np.allclose(outnii_out_temp, outnii_out_cntrl) 


    

