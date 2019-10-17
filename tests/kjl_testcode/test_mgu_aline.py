from ndmg.utils import gen_utils as mgu
import ndmg
from ndmg.utils.reg_utils import align
import numpy as np


inp = '../ndmg_outputs/anat/preproc/t1w_brain_nores.nii.gz'
ref = '/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
xfm = '../ndmg_outputs/tmp/reg_m/xfm_t1w2mni_init.mat'
def test_aline():
    align(inp,
        ref,
        xfm=None,
        out=None,
        dof=12,
        searchrad=True,
        bins=256,
        interp=None,
        cost="mutualinfo",
        sch=None,
        wmseg=None,
        init=None,
        finesearch=None,
    )
    a = np.array(np.loadtxt(xfm))
    outarray = np.array([[1.009304, -0.034007, 0.014804, -3.574831],
                         [-0.026336, 1.046128, 0.149384, -38.406683],
                         [-0.015697, -0.224336, 1.093062, -37.841681],
                         [0.000000, 0.000000, 0.000000, 1.000000]])
    assert np.allclose(a, outarray)