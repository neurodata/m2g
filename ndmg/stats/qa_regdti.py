import os
import re
import sys
import numpy as np
import nibabel as nib
import matplotlib as mpl
mpl.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt

from argparse import ArgumentParser
from matplotlib.colors import colorConverter
from skimage.filters import threshold_otsu
from scipy import ndimage
from matplotlib.colors import LinearSegmentedColormap
from dipy.core.gradients import gradient_table
from dipy.io import read_bvals_bvecs

def save_reg_pngs(fs, outdir, fname=None):
    """
    fs: 4-tuple of paths to regdti, bval, bvec, and atlas files 
    outdir: directory where output png file is saved 
    """
    plt.rcParams.update({'axes.labelsize': 'x-large', 'axes.titlesize':'x-large'})
    fdti, fbval, fbvec, fatlas = fs
    atlas_img = nib.load(fatlas)
    atlas_data = atlas_img.get_data()
    x1 = 78 
    x2 = 90 
    x3 = 100
    y1 = 82
    y2 = 107
    y3 = 142
    z1 = 88
    z2 = 103
    z3 = 107
    img = nib.load(fdti)
    data = img.get_data()
    data = get_b0_vol(data, fbval, fbvec)

    cmap1 = LinearSegmentedColormap.from_list('mycmap1', ['black', 'magenta'])
    cmap2 = LinearSegmentedColormap.from_list('mycmap2', ['black', 'green'])
    
    ax_x1 = plt.subplot(331)
    ax_x1.set_ylabel('Sagittal Slice: Y and Z fixed')
    ax_x1.set_title('X = ' + str(x1))
    ax_x1.yaxis.set_ticks([0, data.shape[2]/2, data.shape[2] - 1 ])
    ax_x1.xaxis.set_ticks([0, data.shape[1]/2, data.shape[1] - 1 ])
    image = data[x1,:,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[x1,:,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_x2 = plt.subplot(332)
    ax_x2.set_title('X = ' + str(x2))
    ax_x2.get_yaxis().set_ticklabels([])
    ax_x2.get_xaxis().set_ticklabels([])
    image = data[x2,:,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[x2,:,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_x3 = plt.subplot(333)
    ax_x3.set_title('X = ' + str(x3))
    ax_x3.get_yaxis().set_ticklabels([])
    ax_x3.get_xaxis().set_ticklabels([])
    image = data[x3,:,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[x3,:,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y1 = plt.subplot(334)
    ax_y1.set_ylabel('Coronal Slice: X and Z fixed')
    ax_y1.set_title('Y = ' + str(y1))
    ax_y1.yaxis.set_ticks([0, data.shape[0]/2, data.shape[0] - 1 ])
    ax_y1.xaxis.set_ticks([0, data.shape[2]/2, data.shape[2] - 1 ])
    image = data[:,y1,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:,y1,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y2 = plt.subplot(335)
    ax_y2.set_title('Y = ' + str(y2))
    ax_y2.get_yaxis().set_ticklabels([])
    ax_y2.get_xaxis().set_ticklabels([])
    image = data[:,y2,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:,y2,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_y3 = plt.subplot(336)
    ax_y3.set_title('Y = ' + str(y3))
    ax_y3.get_yaxis().set_ticklabels([])
    ax_y3.get_xaxis().set_ticklabels([])
    image = data[:,y3,:,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(ndimage.rotate(atlas_data[:,y3,:], 90), interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 90), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    ax_z1 = plt.subplot(337)
    ax_z1.set_ylabel('Axial Slice: X and Y fixed')
    ax_z1.set_title('Z = ' + str(z1))
    ax_z1.yaxis.set_ticks([0, data.shape[0]/2, data.shape[0] - 1 ])
    ax_z1.xaxis.set_ticks([0, data.shape[1]/2, data.shape[1] - 1 ])
    image = data[:,:,z1,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:,:,z1], interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)

    ax_z2 = plt.subplot(338)
    ax_z2.set_title('Z = ' + str(z2))
    ax_z2.get_yaxis().set_ticklabels([])
    ax_z2.get_xaxis().set_ticklabels([])
    image = data[:,:,z2,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:,:,z2], interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)

    ax_z3 = plt.subplot(339)
    ax_z3.set_title('Z = ' + str(z3))
    ax_z3.get_yaxis().set_ticklabels([])
    ax_z3.get_xaxis().set_ticklabels([])
    image = data[:,:,z3,0] 
    min_val, max_val = get_min_max(image)
    plt.imshow(atlas_data[:,:,z3], interpolation='none', cmap=cmap1, alpha=0.5)
    plt.imshow(ndimage.rotate(image, 0), interpolation='none', cmap=cmap2, vmin=min_val, vmax=max_val, alpha=0.5)
    fig = plt.gcf()
    fig.set_size_inches(12.5, 10.5, forward=True)
    if fname == None:
        fname = os.path.split(fdti)[1].split(".")[0] + '.png'
    plt.savefig(outdir + '/' + fname, format='png')
    print(fname + " saved!")

def get_min_max(data):
    min_val = np.percentile(data, 3) 
    max_val = np.percentile(data, 92) 
    return (min_val, max_val)

def get_b0_vol(data, fbval, fbvec):
    bvals, bvecs = read_bvals_bvecs(fbval, fbvec)
    normalize_bvecs(bvecs)
    gtab = gradient_table(bvals, bvecs)
    return data[:, :, :, gtab.b0s_mask]

def normalize_bvecs(bvecs):
    for i in range(bvecs.shape[0]):
        norm = np.linalg.norm(bvecs[i,:])
        if norm != 1 or norm != 0:
            bvecs[i, :] = bvecs[i, :]/norm
        

def main():
    """
    Argument parser and directory crawler. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.
    Required parameters:
        dtifile:
            - path to regdti file 
        bvalfile:
            - path to bval file
        bvecfile:
            - path to bvec file
        atlasfile:
            - path to atlas file
        outdir:
            - output file save directory
    """
    parser = ArgumentParser(description="Generates registration QA images")
    parser.add_argument("dtifile", action="store", help="base directory loc")
    parser.add_argument("bvalfile", action="store", help="base directory loc")
    parser.add_argument("bvecfile", action="store", help="base directory loc")
    parser.add_argument("atlasfile", action="store", help="base directory loc")
    parser.add_argument("outdir", action="store", help="base directory loc")
    result = parser.parse_args()

    if (not os.path.isdir(result.outdir)): os.mkdir(result.outdir)
    save_reg_pngs((result.dtifile, result.bvalfile, result.bvecfile, result.atlasfile), result.outdir)


if __name__ == '__main__':
    main()
