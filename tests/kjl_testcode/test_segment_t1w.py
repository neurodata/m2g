from ndmg.utils.reg_utils import segment_t1w

t1w = '../ndmg_outputs/anat/preproc/t1w_brain.nii.gz'
basename = '../ndmg_outputs/anat/preproc/t1w_seg'


def test_segment_t1w():
    result = segment_t1w(t1w, basename, opts='')
    assert result == {'csf_prob': '../ndmg_outputs/anat/preproc/t1w_seg_pve_0.nii.gz', 'gm_prob': '../ndmg_outputs/anat/preproc/t1w_seg_pve_1.nii.gz', 'wm_prob': '../ndmg_outputs/anat/preproc/t1w_seg_pve_2.nii.gz'}