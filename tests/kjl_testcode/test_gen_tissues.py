import ndmg
from ndmg.utils.bids_utils import name_resource
from ndmg.register.gen_reg import dmri_reg
import numpy as np
import warnings

warnings.simplefilter("ignore")
import os
from nilearn.image import load_img, math_img
from ndmg.utils import gen_utils as mgu
from ndmg.utils import reg_utils as mgru
import warnings

warnings.simplefilter("ignore")
from dipy.io import read_bvals_bvecs
from dipy.core.gradients import gradient_table
from subprocess import Popen, PIPE
import subprocess
import nibabel as nib
import os.path as op
import sys
from nilearn.image import mean_img
from scipy.sparse import lil_matrix
import nibabel as nib
import numpy as np
import nilearn.image as nl

dwi = '../BNU1/sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.nii.gz'
t1w = '../BNU1//sub-0025864/ses-1/dwi/sub-0025864_ses-1_dwi.bval'
atlas = 'desikan'
outdir = '../ndmg_outputs'
fbval = '../ndmg_outputs/dwi/preproc/bval.bval'
fbvec = '../ndmg_outputs/dwi/preproc/bvec.bvec'
dwi_prep = '../ndmg_outputs/dwi/preproc/eddy_corrected_data_reor_RAS_res.nii.gz'
# (dwi_file, outdir) = namer.dirs["output"]["prep_dwi"]
nodif_B0 = '../ndmg_outputs/dwi/preproc/nodif_B0.nii.gz'
nodif_B0_mask = '../ndmg_outputs/dwi/preproc/nodif_B0_bet_mask.nii.gz'
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

namer = name_resource(dwi, t1w, atlas, outdir)

namer.add_dirs_dwi(paths, labels, label_dirs)

test_2 = dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w_in, vox_size,simple=False)
# dmri_reg(namer, nodif_B0, nodif_B0_mask, t1w, vox_size, simple=False)
# test_2.gen_tissue()
# wm_mask_thr = '../ndmg_outputs/anat/preproc/t1w_wm_thr.nii.gz'
print(test_2.wm_mask_thr)
test_2.gen_tissue()

# def test_gen_tissue():
#     test_2.gen_tissue()
#     img = nib.load(wm_mask_thr)
#     print(test_2.wm_mask_thr)
#     img_arr = img.get_fdata()
#     img_arr = np.array(img_arr)
#     print(img_arr)
#     # assert img_arr[80][60] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# test_gen_tissue()
