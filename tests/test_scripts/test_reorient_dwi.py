import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock, MagicMock	
import nibabel as nib
import numpy as np 
import pytest
import os

#create mock namer
namer = MagicMock()

def test_reorient_dwi(tmp_path): 
	d = tmp_path/"sub"
	d.mkdir()
	#set namer to point to temp directory 
	namer.dirs = {'output': {'prep_dwi': d } }

	# define correct input data path
	# /mnt/labbook/output/untracked/dwi/preproc/eddy_corrected_data.nii.gz
	# eddy corrected dwi file
	dwi_prep_in = '../test_data/inputs/reorient_dwi/eddy_corrected_data.nii.gz'
	bvec_scaled_in = '../test_data/inputs/reorient_dwi/bvec_scaled.bvec'


	# define correct output data path 
	# dwi_prep_out_control_path = 

	dwi_prep_out_control_path = '../test_data/outputs/reorient_dwi/eddy_corrected_data_reor_RAS.nii.gz'
	bvec_reor_out_control_path = '../test_data/outputs/reorient_dwi/bvecs_reor.bvec' 

	#load correct outputs
	dwi_prep_out_control  = nib.load(dwi_prep_out_control_path).get_fdata()
	bvec_reor_out_control = np.loadtxt(bvec_reor_out_control_path)

	#call function and save in temp folder
	[temp_dwi_prep_out, temp_bvec_out] = mgu.reorient_dwi(dwi_prep_in, bvec_scaled_in, namer)

	#load outputs
	dwi_prep_out = nib.load(temp_dwi_prep_out).get_fdata()
	bvec_out = np.loadtxt(temp_bvec_out)

	#test dwi_prep and bvec
	assert np.allclose (bvec_out, bvec_reor_out_control)
	assert np.allclose (dwi_prep_out, dwi_prep_out_control)

#requires most up to date pytest for tmp_path to work
