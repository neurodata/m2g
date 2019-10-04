import warnings
import ndmg
warnings.simplefilter("ignore")
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgr
import nibabel as nib
import numpy as np
import nilearn.image as nl
import os
import os.path as op
import pytest

input_dir = r"../test_data/inputs/sub-0025864_ses-1_T1w.nii.gz"
ref_dir = r"../test_data/inputs/MNI152_T1_2mm_brain"
# out_dir = r"/mnt/e/."

def test_align(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    temp_out1 = d / "omat.data"
    temp_out2 = d / "outnii.nii.gz"

    inp = input_dir
    ref = ref_dir
    xfm = temp_out1
    out = temp_out2

    mgr.align(inp, ref, xfm, out)
    # result_nii = nib.load(str(out))
    result_mat = np.loadtxt(str(xfm))
    result_mat = np.array(result_mat)

    ''' output_mat = np.array([[0.8271407155,  -0.04727642977,  0.006816218756,  15.99814178],
                           [-0.005617838577,  0.8770838128,  -0.000978902222,  -0.3486071619],
                           [-0.006664295282,  -0.04974933234,  0.8076537939,  -18.14272133],
                           [0,  0,  0,  1]])  '''

    output_mat = np.array([[ 0.8271407155, -0.04727642977, 0.006816218756, 15.99814178],
    [ -0.005617838577, 0.8770838128, -0.000978902222, -0.3486071619],
    [ -0.006664295282, -0.04974933234, 0.8076537939, -18.14272133],
    [ 0., 0., 0., 1.]])

      
    assert np.allclose(result_mat[3,:], output_mat[3,:]) 


    

