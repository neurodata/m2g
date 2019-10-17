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

# input_dir = r"../test_data/inputs/t1w_brain_nores.nii.gz"
# ref_dir = r"../test_data/ref_inputs/MNI152_T1_2mm_brain.nii.gz"
# xfm_dir = r"../test_data/temp_outputs/xfm_t1w2mni_init.mat"


input_dir = '../ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz'
ref_dir = '/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
xfm_dir = '../ndmg_outputs/tmp/reg_m/xfm_t1w2mni_init.mat'

def test_align_nonlinear(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    temp_out1 = d / "outimage.nii.gz"
    temp_out2 = d / "outcoefficients.nii.gz"

    inp = input_dir
    ref = ref_dir
    xfm = xfm_dir
    out = temp_out1
    warp = temp_out2

    mgr.align_nonlinear(inp, ref, xfm, out, warp)
    img = nib.load(str(warp))
    img_1 = img.get_fdata()
    result_warp = np.array(img_1)
    # result_out = np.array(nib.load(out))
    np.set_printoptions(precision=8)

    out_warp = result_warp.shape
    ref_warp = (25, 30, 25, 3)

    assert out_warp == ref_warp