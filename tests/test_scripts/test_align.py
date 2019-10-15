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
    temp_out1 = d / "omat.data"
    temp_out2 = d / "outnii.nii.gz"
    
    # set input/ouput data paths
    align_in_path = r"../test_data/inputs/align/sub-0025864_ses-1_T1w.nii.gz"
    ref_in_path = r"../test_data/inputs/align/MNI152_T1_2mm_brain.nii.gz"
    omat_out_cntrl_path = r"../test_data/outputs/align/omat.mat"
    
    # call function
    inp = align_in_path
    ref = ref_in_path
    xfm = temp_out1
    out = temp_out2
    mgr.align(inp, ref, xfm, out)
    
    # load function outputs
    omat_out_temp = np.loadtxt(str(xfm))
    
    # load output data
    omat_out_cntrl = np.loadtxt(str(omat_out_cntrl_path))
    
    # assert
    assert np.allclose(omat_out_temp, omat_out_cntrl) 


    

