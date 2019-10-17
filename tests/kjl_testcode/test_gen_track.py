import ndmg
from ndmg.track.gen_track import build_seed_list
import numpy as np

mask_img_file = '../ndmg_outputs/anat/registered/t1w_wm_gm_int_in_dwi.nii.gz'
stream_affine = np.array([[1., 0., 0., 0.],
                          [0., 1., 0., 0.],
                          [0., 0., 1., 0.],
                          [0., 0., 0., 1.]])
dens = 1

def test_build_list():
    result = np.array(build_seed_list(mask_img_file, stream_affine, dens))
    print(result[0])
    output = np.array([72.41428282, 96.60166556, 27.27406591])
    assert np.all(result[0] == output)

# test_build_list()
