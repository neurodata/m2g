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

