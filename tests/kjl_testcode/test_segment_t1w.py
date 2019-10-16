from ndmg.utils.reg_utils import segment_t1w
import pytest
import nibabel as nib
import numpy as np

t1w = '../test_data/inputs/segment_t1w/t1w_brain.nii.gz'

def test_segment_t1w(tmp_path):
    # make a temporary path
    d = tmp_path / "sub"
    d.mkdir()
    d_path = d / "t1w_seg"

    # this is the result when run segment_t1w, and store in the tem_path
    result = segment_t1w(t1w, d_path, opts='')
    output1_data = nib.load(result['csf_prob'])
    output1_data = output1_data.get_fdata()
    output2_data = nib.load(result['gm_prob'])
    output2_data = output2_data.get_fdata()
    output3_data = nib.load(result['wm_prob'])
    output3_data = output3_data.get_fdata()

    # this is the result load from the test_data which run the pipeline produce
    test_data1 = nib.load('../test_data/outputs/segment_t1w/t1w_seg_pve_0.nii.gz').get_fdata()
    test_data2 = nib.load('../test_data/outputs/segment_t1w/t1w_seg_pve_1.nii.gz').get_fdata()
    test_data3 = nib.load('../test_data/outputs/segment_t1w/t1w_seg_pve_2.nii.gz').get_fdata()

    assert np.allclose(output1_data, test_data1)
    assert np.allclose(output2_data, test_data2)
    assert np.allclose(output3_data, test_data3)

