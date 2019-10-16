#Guidelines for Unit Test Structure and Naming:

Imports: Use the following imports and shorthand (only as required):
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

Storing and Loading Data:
1. All stored data paths should belong in '../test_data/(inputs or outputs)/folder_test_name/' + 'filename' (e.g: '../test_data/inputs/reorient_dwi/eddy_corrected_data.nii.gz', '../test_data/outputs/reorient_dwi/eddy_corrected_data.nii.gz') 
2. Temporary outputs from function being tested should belong in a temp directory see (http://doc.pytest.org/en/latest/tmpdir.html). If there are issues and you must save them somewhere, put into '../test_data/temp_outputs/folder_test_name' (e.g)
3. Load bvec data with np.loadtxt().
4. Load nifti images with nibabel.load()
	a. Use nibabel.load().get_fdatat() to load as np.array

Naming:
1. Input Data Variables: 
	a. Path: name + _in_path (e.g dwi_in_path)
	b. Variable (may not be required depending on function) : name + _in (e.g dwi_in),

2. Output Data Variables:
	a. Path: name + _out_cntrl_path (e.g dwi_out_cntrl_path)
	b. Variable: name + _out_cntrl (e.g dwi_out_cntrl)

3. Function Data Variables:
	a. Path:  name + _out_temp_path (e.g dwi_out_temp_path)
	b. Variable: name + out_temp (e.g dwi_out_temp)

Asserts:
1. Compare np.arrays with np.allclose 
2. Compare nifti images by loading with nibabel and comparing as np.array (see above)


General Structure: 

#Import Libraries
...
import nibabel as nib 
import numpy as np
...

#Mocks (if required)

def test_example(tmp_path):
	#create temp directory
	d = tmp_path/"sub"
	d.mkdir()

	#set input/output data paths 
	dwi_in_path = '../test_data/inputs/folder_test_name/some_data'
	...
	dwi_out_cntrl_path = '../test_data/outputs/folder_test_name/some_data'

	#load input/outputs data
	dwi_out_cntrl = nib.load(dwi_out_path).get_fdata()
	...

	#call function
	[dwi_out_temp_path] = test_function(dwi_in_path)
	...

	#load function outputs
	dwi_out_temp = nib.load(dwi_out_temp_path).get_fdata() 
	...

	#assert 
	assert np.allclose(dwi_out_cntrl,dwi_out_temp)
	...