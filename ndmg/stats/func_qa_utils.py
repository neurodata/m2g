# Copyright 2016 NeuroData (http://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# qc.py
# Created by Eric W Bridgeford on 2016-06-08.
# Email: ebridge2@jhu.edu

from numpy import ndarray as nar
from scipy.stats import gaussian_kde
from ndmg.utils import utils as mgu
import numpy as np
import nibabel as nb
import sys
import re
import random as ran
import scipy.stats.mstats as scim
import os.path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly as py
import plotly.offline as offline
from ndmg.timeseries import timeseries as mgts
from ndmg.stats.qa_reg import plot_overlays


def dice_coefficient(a, b):
    """
    dice coefficient 2nt/na + nb.
    Code taken from https://en.wikibooks.org/wiki/Algorithm_Implementation
    /Strings/Dice%27s_coefficient#Python

    ** Positional Arguments:**
        a:
            - the first array.
        b:
            - the second array.
    """
    a = nar.tolist(nar.flatten(a))
    b = nar.tolist(nar.flatten(b))
    if not len(a) or not len(b):
        return 0.0
    if len(a) == 1:
        a = a + u'.'
    if len(b) == 1:
        b = b + u'.'

    a_bigram_list = []
    for i in range(len(a)-1):
        a_bigram_list.append(a[i:i+2])
    b_bigram_list = []
    for i in range(len(b)-1):
        b_bigram_list.append(b[i:i+2])

    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0/float(len(a_bigrams) + len(b_bigrams))
    return dice_coeff


def mse(imageA, imageB):
    """
    the 'Mean Squared Error' between the two images is the
    sum of the squared difference between the two images;
    NOTE: the two images must have the same dimension
    from http://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
    NOTE: we've normalized the signals by the mean intensity at each
    point to make comparisons btwn fMRI and MPRAGE more viable.
    Otherwise, fMRI signal vastly overpowers MPRAGE signal and our MSE
    would have very low accuracy (fMRI signal differences >>> actual
    differences we are looking for).

    **Positional Arguments:**
        imageA:
            - the first image.
        imageB:
            - the second image.
    """
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= (float(imageA.shape[0] * imageA.shape[1]))
    return float(err)


def compute_kdes(before, after, steps=1000):
    """
    A function to plot kdes of the arrays for the similarity between
    the before/reference and after/reference.

    **Positional Arguments:**
        before:
            - a numpy array before an operational step.
        after:
            - a numpy array after an operational step.
    """
    x_min = min(np.nanmin(before), np.nanmin(after))
    x_max = max(np.nanmax(before), np.nanmax(after))
    x_grid = np.linspace(x_min, x_max, steps)
    kdebef = gaussian_kde(before)
    kdeaft = gaussian_kde(after)
    return [x_grid, kdebef.evaluate(x_grid), kdeaft.evaluate(x_grid)]


def hdist(array1, array2):
    """
    A function for computing the hellinger distance between arrays
    1 and 2.

    **Positional Arguments:**
        array1:
            - the first array.
        array2:
            - the second array.
    """
    return np.sqrt(np.sum((np.sqrt(array1) -
                          np.sqrt(array2)) ** 2)) / float(np.sqrt(2))


def percent_overlap(array1, array2):
    """
    A function to compute the degree of overlap between two binarized
    arrays. Assumes that inputs are already appropriately thresholded,
    and are of the desired shape.

    **Positional Arguments:**
        array1:
            - the first array.
        array2:
            - the second array.
    """
    # binarize if not already
    array1[array1 > 0] = 1
    array1[array1 <= 0] = 0
    array2[array2 > 0] = 1
    array2[array2 <= 0] = 0

    if array1.shape != array2.shape:
        raise ValueError("Your overlap arrays are not the same shape.")

    overlap = np.logical_and(array1, array2)
    occupied_space = np.logical_or(array1, array2)
    return overlap.sum()/float(occupied_space.sum())


def registration_score(aligned_func, reference_mask, outdir):
    """
	A function to compute the registration score between two images.

    **Positional Arguments:**
        aligned_func:
        - the brain being aligned. assumed to be a 4d fMRI scan.
        reference_mask:
        - the template being aligned to. assumed to be a 3d mask.
        outdir:
        - the directory in which temporary files will be placed.
    """
    func_name = mgu.get_filename(aligned_func)
    func_brain = mgu.name_tmps(outdir, func_name, "_brain.nii.gz")
    func_mask = mgu.name_tmps(outdir, func_name, "_brain_mask.nii.gz")
    # extract brain and use generous 0.3 threshold with -m mask option
    mgu.extract_brain(aligned_func, func_brain, opts=' -f 0.3 -m')

    func = nb.load(func_mask)
    mask = nb.load(reference_mask)
    fid = mgu.get_filename(aligned_func)

    fdat = func.get_data()
    mdat = mask.get_data()

    prod_im = np.multiply(fdat, mdat)

    if fdat.ndim == 4:
        # if our data is 4d, mean over the temporal dimension
        fdat = fdat.mean(axis=3)

    freg_qual = plot_overlays(mdat, fdat)
    reg_score = percent_overlap(fdat, mdat)
    return (reg_score, freg_qual)




def check_alignments(mri_bname, mri_aname, refname, qcdir,
                     fname, title=""):
    """
    A function to check alignments and generate descriptive statistics
    and plots based on the overlap between two images.

    **Positional Arguments**
        mri_bname:
            - the 4d mri file before an operation has taken place
        mri_aname:
            - the 4d mri file after an operation has taken place
        refname:
            - the 3d file used as a reference for the operation
        qcdir:
            - the output directory for the plots
        title:
            - a string (such as the operation name) for use in the plot
                 titles (defaults to "")
        fname:
            - a string to use in the file handle for easy finding
    """
    print "Performing Quality Control for " + title + "..."
    print "\tBefore " + title + ": " + mri_bname
    print "\tAfter " + title + ": " + mri_aname
    print "\tReference " + title + ": " + refname

    # load the nifti images
    mri_before = nb.load(mri_bname)
    mri_after = nb.load(mri_aname)
    reference = nb.load(refname)

    # resample if not in same image space
    if not all(x in mri_after.header.get_zooms()[:3] for x in
               mri_before.header.get_zooms()[:3]) or not all(x
               in mri_after.header.get_data_shape()[:3] for x in
               mri_before.header.get_data_shape()[:3]):

        mri_tname = qcdir + "/" + fname + "_res.nii.gz"
        from ndmg import register as mgr
        mgr().resample_fsl(mri_bname, mri_tname, refname)
        mri_before = nb.load(mri_tname)

    # load the data contained for each image
    mri_bdata = mri_before.get_data()
    mri_adata = mri_after.get_data()
    refdata = reference.get_data()

    nvols = mri_bdata.shape[3]
    nslices = mri_bdata.shape[2]

    v_bef = []
    v_aft = []

    refdata = np.divide(refdata, np.mean(refdata) + 1)
    for t in range(0, nvols):
        mribefdat = np.divide(mri_bdata[:, :, :, t],
                              np.mean(mri_bdata[:, :, :, t]) + 1)
        mriaftdat = np.divide(mri_adata[:, :, :, t],
                              np.mean(mri_adata[:, :, :, t]) + 1)
        for s in range(0, nslices):
            v_bef.append(tuple((s + ran.random(),
                                self.mse(mribefdat[:, :, s],
                                         refdata[:, :, s]))))
            v_aft.append(tuple((s + ran.random(),
                                self.mse(mriaftdat[:, :, s],
                                         refdata[:, :, s]))))

    kdes = self.compute_kdes(zip(*v_bef)[1], zip(*v_aft)[1])

    xlim = tuple((0, np.nanmax(kdes[0])))
    ylim = tuple((0, max(np.nanmax(kdes[1]), np.nanmax(kdes[2]))))
    axkde_list = []
    axkde_list.append(py.graph_objs.Scatter(x=kdes[0], y=kdes[1],
                      fillcolor='(0, 0, 255, 1)', mode='lines',
                      name='before mean = %.2E' % np.mean(zip(*v_bef)[1])))
    axkde_list.append(py.graph_objs.Scatter(x=kdes[0], y=kdes[2],
                      fillcolor='(255, 0, 0, 1)', mode='lines',
                      name='after mean = %.2E' % np.mean(zip(*v_aft)[1])))
    layout = dict(title=title +
                  (" Hellinger Distance = %.4E" %
                   self.hdist(zip(*v_bef)[1], zip(*v_aft)[1])),
                  xaxis=dict(title='MSE', range=xlim),
                  yaxis=dict(title='Density', range=ylim))
    fkde = dict(data=axkde_list, layout=layout)
    path = qcdir + "/" + fname + "_kde.html"
    offline.plot(fkde, filename=path, auto_open=False)

    xlim = tuple((0, nslices + 1))
    ylim = tuple((0, max(np.nanmax(zip(*v_bef)[1]),
                         np.nanmax(zip(*v_aft)[1]))))
    axjit_list = []
    axjit_list.append(py.graph_objs.Scatter(x=zip(*v_bef)[0],
                      y=zip(*v_bef)[1],
                      name='before mean = %.2E' % np.mean(zip(*v_bef)[1]),
                      marker=dict(size=3.0, color='rgba(0, 0, 255, 1)'),
                      mode='markers'))
    axjit_list.append(py.graph_objs.Scatter(x=zip(*v_aft)[0],
                      y=zip(*v_aft)[1],
                      name='after mean = %.2E' % np.mean(zip(*v_aft)[1]),
                      marker=dict(size=3.0, color='rgba(255, 0, 0, 1)'),
                      mode='markers'))
    layout = dict(title="Jitter Plot showing slicewise impact of " +
                  title,
                  xaxis=dict(title='Slice Number', range=xlim),
                  yaxis=dict(title='MSE', range=ylim))
    fjit = dict(data=axjit_list, layout=layout)
    path = qcdir + "/" + fname + "_jitter.html"
    offline.plot(fjit, filename=path, auto_open=False)
    pass


def opaque_colorscale(basemap, reference, alpha=0.5):
    """
    A function to return a colorscale, with opacities
    dependent on reference intensities.

    **Positional Arguments:**
        - basemap:
            - the colormap to use for this colorscale.
        - reference:
            - the reference matrix.
    """
    cmap = basemap(reference)
    # all values beteween 0 opacity and .6
    denom = np.nanmax(reference)
    if denom == 0:  # avoid divide by zero
         denom = 1
    opaque_scale = alpha*reference/float(denom)
    # remaps intensities
    cmap[:, :, 3] = opaque_scale
    return cmap


def expected_variance(s, n, qcdir, scanid="", title=""):
    """
    A function to show the expected variance of each component
    in nuisance regression.

    **Positional Arguments:**
        - s:
            - an array of the variance of each component, or the
              eigenvalues computed in SVD/eigendecomposition for each
              component (should be sorted by variance).
        - n:
            - the number of components chosen for compcor.
        - qcdir:
            - the directory to place outputs in.
        - scanid:
            - the id of the particular subject.
        - title:
            - the method being employed that an expected variance
              plot is neede for. Examples are "CompCor" or "PCA".
    """
    # normalize so that it sums to one
    s = s/np.sum(s)
    total_var = np.cumsum(s)
    # the variance accounted for by the top used components
    var_acct = total_var[n-1]

    colors = ['rgba(255,0, 0,1)'] * s.shape[0]
    colors[n] = 'rgba(26,200,255,1)'
    axvar = [py.graph_objs.Bar(x=range(s.shape[0]), y=s,
             marker=dict(color=colors))]
    layout = dict(title=" ".join([title, "Scree Plot,", "N=", str(n),
                                  ",", "Var=", str(var_acct)]),
                  xaxis=dict(title='Component'),
                  yaxis=dict(title='Variance'))
    fvar = dict(data=axvar, layout=layout)
    offline.plot(fvar, filename=str(qcdir + "/" + scanid + "_scree.html"),
                 auto_open=False)


def mask_align(mri_data, ref_data, qcdir, scanid="", refid=""):
    """
    A function to produce an image showing the alignments of two
    reference images for checking mask alignments.

    **Positional Arguments:**
        mri_image:
            - the first matrix.
        ref_image:
            - the reference matrix.
        qcdir:
            - the path to a directory to dump the outputs.
        scan_id:
            - the id of the scan being analyzed.
        refid:
            - the id of the reference being analyzed.
    """
    cmd = "mkdir -p " + qcdir
    mgu.execute_cmd(cmd)
    mri_data = mgu.get_braindata(mri_data)
    ref_data = mgu.get_braindata(ref_data)

    # if we have 4d data, np.mean() to get 3d data
    if len(mri_data.shape) == 4:
        mri_data = np.nanmean(mri_data, axis=3)

    falign = plt.figure()

    depth = mri_data.shape[2]

    depth_seq = np.unique(np.round(np.linspace(0, depth-1, 25)))
    nrows = np.ceil(np.sqrt(depth_seq.shape[0]))
    ncols = np.ceil(depth_seq.shape[0]/float(nrows))

    # produce figures for each slice in the image
    for d in range(0, depth_seq.shape[0]):
        # TODO EB: create nifti image with these values
        # and allow option to add overlap with mni vs mprage
        i = depth_seq[d]
        axalign = falign.add_subplot(nrows, ncols, d+1)
        axalign.imshow(self.opaque_colorscale(matplotlib.cm.Blues,
                                              mri_data[:, :, i], 0.6))
        axalign.imshow(self.opaque_colorscale(matplotlib.cm.Reds,
                                              ref_data[:, :, i], 0.4))
        axalign.set_xlabel('Position (res)')
        axalign.set_ylabel('Position (res)')
        axalign.set_title('%d slice' % i)
    falign.set_size_inches(nrows*6, ncols*6)
    falign.tight_layout()
    fname = qcdir + "/" + scanid + "_" + refid + "_overlap.png"
    falign.savefig(fname)
    plt.close(falign)
    # return the figpath so we can save it back to the html
    return fname


def image_align(mri_data, ref_data, qcdir, scanid="", refid=""):
    """
    A function to produce an image showing the alignments of two
    reference images.

    **Positional Arguments:**
        mri_image:
            - the first matrix.
        ref_image:
            - the reference matrix.
        qcdir:
            - the path to a directory to dump the outputs.
        scan_id:
            - the id of the scan being analyzed.
        refid:
            - the id of the reference being analyzed.
    """
    cmd = "mkdir -p " + qcdir
    mgu.execute_cmd(cmd)
    mri_data = mgu.get_braindata(mri_data)
    ref_data = mgu.get_braindata(ref_data)

    # if we have 4d data, np.mean() to get 3d data
    if len(mri_data.shape) == 4:
        mri_data = np.nanmean(mri_data, axis=3)

    falign = plt.figure()

    depth = mri_data.shape[2]

    depth_seq = np.unique(np.round(np.linspace(0, depth - 1, 25))).astype(int)
    nrows = np.ceil(np.sqrt(depth_seq.shape[0]))
    ncols = np.ceil(depth_seq.shape[0]/float(nrows))

    # produce figures for each slice in the image
    for d in range(0, depth_seq.shape[0]):
        # TODO EB: create nifti image with these values
        # and allow option to add overlap with mni vs mprage
        i = depth_seq[d]
        axalign = falign.add_subplot(nrows, ncols, d+1)
        axalign.imshow(self.opaque_colorscale(matplotlib.cm.Blues,
                                              mri_data[:, :, i]))
        axalign.imshow(self.opaque_colorscale(matplotlib.cm.Reds,
                                              ref_data[:, :, i]))
        axalign.set_xlabel('Position (res)')
        axalign.set_ylabel('Position (res)')
        axalign.set_title('%d slice' % i)
    falign.set_size_inches(nrows*6, ncols*6)
    falign.tight_layout()
    fname = qcdir + "/" + scanid + "_" + refid + "_overlap.png"
    falign.savefig(fname)
    plt.close(falign)
    # return the figpath so we can save it back to the html
    return fname


def plot_timeseries(timeseries, qcdir=None):
    """
    A function to generate a plot of the timeseries
    of the particular ROI. Makes sure nothing nonsensical is
    happening here.

    **Positional Arguments:**
        - timeseries:
            - the path to a roi timeseries.
        - qcdir:
            - the directory to place quality control figures.
    """
    scan = mgu.get_filename(timeseries)
    path = "{}/{}".format(qcdir, scan)
    fname_ts = "{}_timeseries.html".format(path)
    fname_corr = "{}_corr.png".format(path)

    timeseries = mgts().load_timeseries(timeseries)

    fts_list = []
    for d in range(0, timeseries.T.shape[1]):
        fts_list.append(py.graph_objs.Scatter(
                        x=range(0, timeseries.T.shape[0]),
                        y=timeseries.T[:, d], mode='lines'))

    layout = dict(title=" ".join([scan, "ROI Timeseries"]),
                  xaxis=dict(title='Time Point (TRs)',
                             range=[0, timeseries.T.shape[0]]),
                  yaxis=dict(title='Intensity'),
                  showlegend=False)  # height=405, width=720)
    fts = dict(data=fts_list, layout=layout)
    # py.plotly.image.save_as(fts, filename=fname_ts)
    offline.plot(fts, filename=fname_ts, auto_open=False)

    fcorr = plt.figure()
    axcorr = fcorr.add_subplot(111)
    cax = axcorr.imshow(np.corrcoef(timeseries), interpolation='nearest',
                        cmap=plt.cm.ocean)
    fcorr.colorbar(cax, fraction=0.046, pad=0.04)
    axcorr.set_title(" ".join([scan, "Corr"]))
    axcorr.set_xlabel('ROI')
    axcorr.set_ylabel('ROI')

    fcorr.set_size_inches(10, 10)
    fcorr.tight_layout()
    fcorr.savefig(fname_corr)
    plt.close(fcorr)
    pass
