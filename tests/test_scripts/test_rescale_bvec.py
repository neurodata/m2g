<<<<<<< HEAD
import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock
import numpy as np 
import pytest
import os

#requires most up to date pytest for tmp_path to work
def test_rescale_bvac(tmp_path):
	#create temp file dir
	d = tmp_path/"sub"
	d.mkdir()

	#create temp output dir
	bvec_out_temp1_path = d/ "test1_new.bvec"
	bvec_out_temp2_path = d/ "test2_new.bvec"

	bvec_in1_path = '../test_data/inputs/rescale_bvec/rescale_bvec_test_1.bvec' 
	bvec_in2_path = '../test_data/inputs/rescale_bvec/rescale_bvec_test_2.bvec'
 
	bvec_out_cntrl_path = '../test_data/outputs/rescale_bvec/rescale_bvec_output.bvec'

	#load data
	bvec_out_cntrl= np.loadtxt(bvec_out_cntrl_path)

	#run through data
	mgp.rescale_bvec(bvec_in1_path,str(bvec_out_temp1_path))
	mgp.rescale_bvec(bvec_in2_path,str(bvec_out_temp2_path))

	#open data 
	bvec_out_temp1 = np.loadtxt(str(bvec_out_temp1_path))
	bvec_out_temp2 = np.loadtxt(str(bvec_out_temp2_path))

	assert np.allclose(bvec_out_temp1,bvec_out_cntrl) 
	assert np.allclose(bvec_out_temp2,bvec_out_cntrl)

=======
import pytest
import ndmg
import numpy as np
import warnings

warnings.simplefilter("ignore")
import os.path as op

# def rescale_bvec(bvec, bvec_new):
#
#     bv1 = np.array(np.loadtxt(bvec))
#     # Enforce proper dimensions
#     bv1 = bv1.T if bv1.shape[0] == 3 else bv1
#
#     # Normalize values not close to norm 1
#     bv2 = [
#         b / np.linalg.norm(b) if not np.isclose(np.linalg.norm(b), 0) else b
#         for b in bv1
#     ]
#
#     try:
#         assert "bvec" in bvec_new
#         np.savetxt(bvec_new, bv2)
#         pass
#     except AssertionError:
#         print(
#             "Error: your new b-vector file must have extension .bvec to"
#             + " be compatible with the the pipeline."
#         )
#         pass
#     else:
#         pass
#     pass


def test_rescale_bvec(tmp_path):
    d = tmp_path/"sub"
    d.mkdir()
    test_input = d / "text_input.bvec"
    test_output = d / "text_output.bvec"
    test_input_array = np.array([[1, 2, 3],
                                 [4, 5, 6],
                                 [7, 8, 9]])
    np.savetxt(test_input, test_input_array)
    ndmg.preproc.rescale_bvec(str(test_input), str(test_output))
    test_output_array = np.array(np.loadtxt(str(test_output)))
    b = np.array([[1.230914909793327239e-01, 4.923659639173308955e-01, 8.616404368553290949e-01],
                  [2.073903389460850510e-01, 5.184758473652126831e-01, 8.295613557843402042e-01],
                  [2.672612419124243965e-01, 5.345224838248487931e-01, 8.017837257372731896e-01]])
    assert np.allclose(test_output_array, b)
>>>>>>> be6a5ed560925ea6f3478eb71c567439e6790bb0

