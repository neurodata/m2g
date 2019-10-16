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

def test_align_nonlinear(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    temp_out1 = d / "outimage.nii.gz"
    temp_out2 = d / "outcoefficients.nii.gz"

    # set input data
    alignnonlinear_in_path = r"../test_data/inputs/alignnonlinear/t1w_brain_nores.nii.gz"
    ref_in_path = r"../test_data/inputs/alignnonlinear/MNI152_T1_2mm_brain.nii.gz"
    xfm_in_path = r"../test_data/inputs/alignnonlinear/xfm_t1w2mni_init.mat"
    alignnonlinear_out_cntrl_path = r"../test_data/outputs/alignnonlinear/outcoefficients.nii.gz"

    # call function
    inp = alignnonlinear_in_path
    ref = ref_in_path
    xfm = xfm_in_path
    out = temp_out1
    warp = temp_out2
    mgr.align_nonlinear(inp, ref, xfm, out, warp)

    # load function data
    alignnonlinear_out_temp = nib.load(str(warp)).get_fdata()
    
    # load output data
    alignnonlinear_out_cntrl = nib.load(str(alignnonlinear_out_cntrl_path)).get_fdata()

    assert np.allclose(alignnonlinear_out_cntrl, alignnonlinear_out_temp)
