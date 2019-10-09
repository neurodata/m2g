import ndmg
import numpy as np
from ndmg.register.gen_reg import DmriReg
from ndmg.utils.bids_utils import name_resource


nodif_B0 = '../ndmg_outputs/dwi/preproc/nodif_B0.nii.gz'
nodif_B0_mask = '../ndmg_outputs/dwi/preproc/nodif_B0_bet_mask.nii.gz'
t1w_in = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
vox_size = '2mm'
dwi = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
t1w = '../BNU1//sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
atlas = 'desikan'
outdir = '../ndmg_outputs'

namer = name_resource(dwi, t1w, atlas, outdir)
test_1 = DmriReg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple=False)

def test_tissue2dwi_align():
    test_1.tissue2dwi_align()
    a = np.array(np.loadtxt(test_1.xfm_roi2mni_init))
    outarray = np.array([[1.30201748e-01, -1.82806115e-01, -9.74489331e-01, 1.77111309e+02],
                         [3.79709005e-02, 9.83054222e-01, -1.79339507e-01, 1.51448375e+01],
                         [9.90760194e-01, -1.36519317e-02, 1.34936684e-01, -3.70971904e+01],
                         [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    assert np.allclose(a, outarray)