import warnings
warnings.simplefilter("ignore")
import sys
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mping
import skimage.io as io
import nilearn.image as nl
import os
import os.path as op
#from ndmg.scripts import ndmg_dwi_pipeline

def _tile_plot(imgs, titles, **kwargs):
    """
    Helper function, plot a 3*3 image of overlay_registration
    """
    # Create a new figure and plot the three images
    # plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=1, hspace=1)
    fig, ax = plt.subplots(3, 3)
    k = 0
    for i in [0, 1, 2]:
        for j in [0, 1, 2]:
            # ax[i][j].set_axis_off()
            ax[i][j].imshow(imgs[k], **kwargs)
            ax[i][j].set_title(titles[k])
            k = k+1
    
    return fig

def overlay_slices(L, R, slice_index=None, slice_type=1, ltitle='Left',
                   rtitle='Right', fname=None):
    r"""Plot three overlaid slices from the given volumes.
    Creates a figure containing three images: the gray scale k-th slice of
    the first volume (L) to the left, where k=slice_index, the k-th slice of
    the second volume (R) to the right and the k-th slices of the two given
    images on top of each other using the red channel for the first volume and
    the green channel for the second one. It is assumed that both volumes have
    the same shape. The intended use of this function is to visually assess the
    quality of a registration result.
    Parameters
    ----------
    L : array, shape (S, R, C)
        the first volume to extract the slice from, plottet to the left
    R : array, shape (S, R, C)
        the second volume to extract the slice from, plotted to the right
    slice_index : int (optional)
        the index of the slices (along the axis given by slice_type) to be
        overlaid. If None, the slice along the specified axis is used
    slice_type : int (optional)
        the type of slice to be extracted:
        0=sagital, 1=coronal (default), 2=axial.
    ltitle : string (optional)
        the string to be written as title of the left image. By default,
        no title is displayed.
    rtitle : string (optional)
        the string to be written as title of the right image. By default,
        no title is displayed.
    fname : string (optional)
        the name of the file to write the image to. If None (default), the
        figure is not saved to disk.
    """
    # Normalize the intensities to [0,255]
    sh = L.shape
    L = np.asarray(L, dtype=np.float64)
    R = np.asarray(R, dtype=np.float64)
    L = 255 * (L - L.min()) / (L.max() - L.min())
    R = 255 * (R - R.min()) / (R.max() - R.min())
    # Create the color image to draw the overlapped slices into, and extract
    # the slices (note the transpositions)
    if slice_type is 0:
        if slice_index is None:
            slice_index = sh[0] // 2
        colorImage = np.zeros(shape=(sh[2], sh[1], 3), dtype=np.uint8)
        ll = np.asarray(L[slice_index, :, :]).astype(np.uint8).T
        rr = np.asarray(R[slice_index, :, :]).astype(np.uint8).T
    elif slice_type is 1:
        if slice_index is None:
            slice_index = sh[1] // 2
        colorImage = np.zeros(shape=(sh[2], sh[0], 3), dtype=np.uint8)
        ll = np.asarray(L[:, slice_index, :]).astype(np.uint8).T
        rr = np.asarray(R[:, slice_index, :]).astype(np.uint8).T
    elif slice_type is 2:
        if slice_index is None:
            slice_index = sh[2] // 2
        colorImage = np.zeros(shape=(sh[1], sh[0], 3), dtype=np.uint8)
        ll = np.asarray(L[:, :, slice_index]).astype(np.uint8).T
        rr = np.asarray(R[:, :, slice_index]).astype(np.uint8).T
    else:
        print("Slice type must be 0, 1 or 2.")
        return
    # Draw the intensity images to the appropriate channels of the color image
    # The "(ll > ll[0, 0])" condition is just an attempt to eliminate the
    # background when its intensity is not exactly zero (the [0,0] corner is
    # usually background)
    colorImage[..., 0] = ll * (ll > ll[0, 0])
    colorImage[..., 1] = rr * (rr > rr[0, 0])
    return colorImage

def qa_align(inp_dir_reg, inp_dir_ref, out_dir):
    """
    inp_dir_reg: directory where output tmp image registered is saved
    inp_dir_ref: directory where input reference image is saved
    out_dir: directory where the final result is saved
    """
    # name new files
    new_name_reg = inp_dir_reg.split('/')[-1]
    new_name_ref = inp_dir_ref.split('/')[-1]
    new_name_qa = new_name_reg.split('.')[0] + ".png"

    # set the output file path of overlay_qa and nifti_result
    out_dir_visual = "{}/qa/reg/".format(out_dir)
    out_dir_tmp_align = "{}/qa/reg/".format(out_dir)+"{}".format(new_name_reg)
    out_dir_tmp_ref = "{}/qa/reg/".format(out_dir)+"{}".format(new_name_ref)
    out_dir_tmp_qa = "{}/qa/reg/".format(out_dir)+"{}".format(new_name_qa)
    
    # load input images of registration and reference
    img_tmp_align_1 = nib.load(inp_dir_reg)
    img_tmp_ref_1 = nib.load(inp_dir_ref)
    img_tmp_align = img_tmp_align_1.get_data()
    img_tmp_ref = img_tmp_ref_1.get_data()

    # save nifti image file
    nib.save(img_tmp_align_1, out_dir_tmp_align)
    nib.save(img_tmp_ref_1, out_dir_tmp_ref)
    
    # create qa image
    shape = img_tmp_align.shape
    x = shape[0] // 2
    y = shape[1] // 2
    z = shape[2] // 2
    imgs = []
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, x-8, 0))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, x, 0))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, x+8, 0)) 
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, y-8, 1))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, y, 1))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, y+8, 1)) 
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, z-8, 2))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, z, 2))
    imgs.append(overlay_slices(img_tmp_ref, img_tmp_align, z+8, 2)) 
    
    # imgs = qa_align(, input_2, output_dir)
    _tile_plot(imgs,['X=40','X=48','X=56','Y=54','Y=64','Y=74','Z=54','Z=64','Z=74'])
    plt.savefig(out_dir_tmp_qa)