import nibabel as nib
import skimage.io as io
import numpy as np


str = '../ndmg_outputs/anat/preproc/t1w_brain.nii.gz'

img = nib.load(str)
print(img.shape)

img_arr = img.get_fdata()
# img_arr = np.squeeze(img_arr)
io.imshow(img_arr[46])