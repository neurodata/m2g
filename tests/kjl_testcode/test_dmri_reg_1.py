import ndmg
import numpy as np
from ndmg.register.gen_reg import dmri_reg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock, MagicMock
namer = MagicMock()
import pytest



def test_tissue2dwi_align(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    test_1 = dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple=False)
    namer.dirs = {'property1': {'property2': d}}
    test_1.tissue2dwi_align()
    a = np.array(np.loadtxt(test_1.xfm_roi2mni_init))
    outarray = np.array([[1.30201748e-01, -1.82806115e-01, -9.74489331e-01, 1.77111309e+02],
                         [3.79709005e-02, 9.83054222e-01, -1.79339507e-01, 1.51448375e+01],
                         [9.90760194e-01, -1.36519317e-02, 1.34936684e-01, -3.70971904e+01],
                         [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    assert np.allclose(a, outarray)


# nodif_B0 = '../ndmg_outputs/dwi/preproc/nodif_B0.nii.gz'
# nodif_B0_mask = '../ndmg_outputs/dwi/preproc/nodif_B0_bet_mask.nii.gz'
# t1w_in = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
# vox_size = '2mm'
# dwi = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
# t1w = '../BNU1//sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
# atlas = 'desikan'
# outdir = '../ndmg_outputs'
# paths = {
#     "prep_dwi": "dwi/preproc",
#     "prep_anat": "anat/preproc",
#     "reg_anat": "anat/registered",
#     "fiber": "dwi/fiber",
#     "tensor": "dwi/tensor",
#     "conn": "dwi/roi-connectomes"
# }
# labels = ['/ndmg_atlases/atlases/label/Human/desikan_space-MNI152NLin6_res-2x2x2.nii.gz']
# label_dirs = ["conn"]
#
# namer = name_resource(dwi, t1w, atlas, outdir)
# namer.add_dirs_dwi(paths, labels, label_dirs)
# test_1 = dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple=False)
#
