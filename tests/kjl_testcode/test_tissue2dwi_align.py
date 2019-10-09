import warnings

warnings.simplefilter("ignore")
from nilearn.image import load_img, math_img
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgru
from bids import BIDSLayout
import re
from itertools import product
import boto3
from ndmg.utils import gen_utils as mgu
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

# Standard Library
import os
import shutil
import time
from datetime import datetime
from subprocess import Popen

# External Packages
import numpy as np
import nibabel as nib
from dipy.tracking.streamline import Streamlines

# Internal Imports
import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg

# dwi = '/mnt/d/Downloads/neurodatadesign/BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
dwi = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
# t1w = '/mnt/d/Downloads/neurodatadesign/BNU1//sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
t1w = '../BNU1//sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
atlas = 'desikan'
# outdir = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs'
outdir = '../ndmg_outputs'


# fbval = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs/dwi/preproc/bval.bval'
fbval = '../ndmg_outputs/dwi/preproc/bval.bval'
# fbvec = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs/dwi/preproc/bvec.bvec'
fbvec = '../ndmg_outputs/dwi/preproc/bvec.bvec'
# dwi_prep = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs/dwi/preproc/eddy_corrected_data_reor_RAS_res.nii.gz'
dwi_prep = '../ndmg_outputs/dwi/preproc/eddy_corrected_data_reor_RAS_res.nii.gz'
# (dwi_file, outdir) = namer.dirs["output"]["prep_dwi"]
# nodif_B0 = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs/dwi/preproc/nodif_B0.nii.gz'
nodif_B0 = '../ndmg_outputs/dwi/preproc/nodif_B0.nii.gz'
# nodif_B0_mask = '/mnt/d/Downloads/neurodatadesign/ndmg_outputs/dwi/preproc/nodif_B0_bet_mask.nii.gz'
nodif_B0_mask = '../ndmg_outputs/dwi/preproc/nodif_B0_bet_mask.nii.gz'
# t1w_in = '/mnt/d/Downloads/neurodatadesign/BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
t1w_in = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
vox_size = '2mm'

paths = {
    "prep_dwi": "dwi/preproc",
    "prep_anat": "anat/preproc",
    "reg_anat": "anat/registered",
    "fiber": "dwi/fiber",
    "tensor": "dwi/tensor",
    "conn": "dwi/roi-connectomes"
}
labels = ['/ndmg_atlases/atlases/label/Human/desikan_space-MNI152NLin6_res-2x2x2.nii.gz']
label_dirs = ["conn"]

from ndmg.utils.bids_utils import flatten
import ndmg.register.gen_reg
from ndmg.utils.bids_utils import name_resource
from ndmg.utils.gen_utils import make_gtab_and_bmask

namer = name_resource(dwi, t1w, atlas, outdir)
# namer = name_resource(dwi, t1w, atlas, outdir)

# [gtab, nodif_B0, nodif_B0_mask] = mgu.make_gtab_and_bmask(
#     fbval, fbvec, dwi_prep, namer.dirs["output"]["prep_dwi"]
# )

namer.add_dirs_dwi(paths, labels, label_dirs)

test_tissue2dwi_align_result = DmriReg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size, simple=False)

# runniii = DmriReg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size,simple=False)
# dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w, vox_size, simple=False)

# runniii.tissue2dwi_align()

def test_tissue2dwi_align():
    # runniii.tissue2dwi_align()
    test_tissue2dwi_align_result()
    a = np.array(np.loadtxt(test_tissue2dwi_align_result.xfm_roi2mni_init))
    outarray = np.array([[ 1.30201748e-01, -1.82806115e-01, -9.74489331e-01,  1.77111309e+02],
                        [3.79709005e-02,  9.83054222e-01, -1.79339507e-01,  1.51448375e+01],
                        [9.90760194e-01, -1.36519317e-02,  1.34936684e-01, -3.70971904e+01],
                        [0.00000000e+00, 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
    assert np.allclose(a, outarray)

