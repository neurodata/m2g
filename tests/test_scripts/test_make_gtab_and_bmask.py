import ndmg
from ndmg import preproc as mgp

from ndmg.utils import gen_utils as mgu
#use if want to test non_fsl version
#import non_fsl_make_gtab_and_bmask as mgu

from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock
import nibabel as nib
import numpy as np 
import pytest
import os


def test_make_gtab_and_bmask(tmp_path): 
	d = tmp_path/"sub"
	d.mkdir()

	#define correct input data path
	fbval_in_path = '../test_data/inputs/make_gtab_and_bmask/bval.bval'
	fbvec_in_path = '../test_data/inputs/make_gtab_and_bmask/bvec.bvec'
	dwi_prep_in_path = '../test_data/inputs/make_gtab_and_bmask/eddy_corrected_data_reor_RAS_res.nii.gz'

	#create temp user directory to store function outputs
	#can't use pytest temp directory b.c fsl commands will fail to interact with it
	# outdir = d/ "temp_data"
	outdir = '../test_data/temp_outputs/make_gtab_and_bmask'

	#define correct output data path 
	# stored as a numpy array 
	grad_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/gtab_grad'
	bvals_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/gtab_bvals'
	bvecs_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/gtab_bvecs'
	b0s_mask_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/gtab_b0s_mask'
	b0_threshold_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/gtab_b0_threshold'

	nodif_B0_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/nodif_B0.nii.gz'
	nodif_B0_mask_out_cntrl_path = '../test_data/outputs/make_gtab_and_bmask/nodif_B0_bet_mask.nii.gz'

	#load control data
	#each property of gtab object 
	#unable to directly save unique dipy Gradient Table Class
	gtab_grad_out_cntrl = np.loadtxt(grad_out_cntrl_path)
	gtab_bvals_out_cntrl = np.loadtxt(bvals_out_cntrl_path)
	gtab_bvecs_out_cntrl = np.loadtxt(bvecs_out_cntrl_path)
	gtab_b0s_mask_out_cntrl = np.loadtxt(b0s_mask_out_cntrl_path)
	gtab_b0_threshold_out_cntrl = np.loadtxt(b0_threshold_out_cntrl_path)

	nodif_B0_out_cntrl = nib.load(nodif_B0_out_cntrl_path).get_fdata()
	nodif_B0_mask_out_cntrl = nib.load(nodif_B0_mask_out_cntrl_path).get_fdata()

	#call function
	[gtab, nodif_B0_out_temp_path, nodif_B0_mask_out_temp_path] = mgu.make_gtab_and_bmask(fbval_in_path, fbvec_in_path, dwi_prep_in_path, outdir)

	#call out nodif_B0 and nodif_B0_mask as np.arrays
	nodif_B0_out_temp = nib.load(nodif_B0_out_temp_path).get_fdata()
	nodif_B0_mask_out_temp = nib.load(nodif_B0_mask_out_temp_path).get_fdata()

	#test gtab properties
	assert np.allclose (gtab.gradients, gtab_grad_out_cntrl)
	assert np.allclose (gtab.bvals, gtab_bvals_out_cntrl)
	assert np.allclose (gtab.bvecs, gtab_bvecs_out_cntrl)
	assert np.allclose (gtab.b0s_mask, gtab_b0s_mask_out_cntrl)
	assert gtab.b0_threshold ==  gtab_b0_threshold_out_cntrl

	print(nodif_B0_out_temp_path)
	print(nodif_B0_mask_out_temp_path)

	#test b0
	assert np.allclose (nodif_B0_out_temp, nodif_B0_out_cntrl)
	assert np.allclose (nodif_B0_mask_out_temp, nodif_B0_mask_out_cntrl)



