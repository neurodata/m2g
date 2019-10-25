import ndmg
from ndmg import preproc
from ndmg import register
from ndmg import track
from ndmg import graph
from ndmg.utils import gen_utils
from ndmg.utils import reg_utils
from ndmg.utils import cloud_utils
from unittest.mock import Mock, MagicMock	
import nibabel as nib
import numpy as np 
import pytest
import os

#create mock namer
namer = MagicMock()

#requires most up to date pytest for tmp_path to work
def test_reorient_image(tmp_path): 
	d = tmp_path/"sub"
	d.mkdir()
	#set namer to point to temp directory 
	namer.dirs = {'output': {'prep_anat': d } }

	# define correct input data path
	# /mnt/labbook/output/untracked/dwi/preproc/eddy_corrected_data.nii.gz
	# eddy corrected dwi file
	img_in_path = '../test_data/inputs/reorient_image/sub-0025864_ses-1_T1w.nii.gz' 

	# define correct output data path 
	t1w_out_cntrl_path = '../test_data/outputs/reorient_image/sub-0025864_ses-1_T1w_reor_RAS.nii.gz' 

	#load correct outputs
	t1w_out_cntrl = nib.load(t1w_out_cntrl_path).get_fdata()

	#call function and save in temp folder
	t1w_out_temp_path = gen_utils.reorient_img(img_in_path, namer)

	#load outputs
	t1w_out_temp = nib.load(t1w_out_temp_path).get_fdata()

	#test dwi_prep and bvec
	assert np.allclose (t1w_out_temp, t1w_out_cntrl)


