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
import numpy as np
from scipy.stats import gaussian_kde
from subprocess import Popen, PIPE
import nibabel as nb
import sys
import re
import random as ran
import scipy.stats.mstats as scim
import os.path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ndmg.utils import utils as mgu


class qc(object):

    def __init__(self):
        """
        Enables quality control of fMRI and DTI processing pipelines.
        """
        pass

    def dice_coefficient(self, a, b):
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

    def mse(self, imageA, imageB):
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

    def compute_kdes(self, before, after, steps=1000):
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

    def hdist(self, array1, array2):
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

    def check_alignments(self, mri_bname, mri_aname, refname, qcdir,
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
        if not all(x in mri_after.get_header().get_zooms()[:3] for x in
                   mri_before.get_header().get_zooms()[:3]):

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
        fkde = plt.figure()
        axkde = fkde.add_subplot(111)
        axkde.plot(kdes[0], kdes[1])
        axkde.plot(kdes[0], kdes[2])
        axkde.set_title(title + (" Hellinger Distance = %.4E" %
                        self.hdist(zip(*v_bef)[1], zip(*v_aft)[1])))
        axkde.set_xlabel('MSE')
        xlim = tuple((0, np.nanmax(kdes[0])))
        ylim = tuple((0, max(np.nanmax(kdes[1]), np.nanmax(kdes[2]))))
        axkde.set_xlim(xlim)
        axkde.set_ylim(ylim)
        axkde.set_ylabel('Density')
        axkde.legend(['before, mean = %.2E' % np.mean(zip(*v_bef)[1]),
                     'after, mean = %.2E' % np.mean(zip(*v_aft)[1])])
        fnamekde = qcdir + "/" + fname + "_kde.png"
        fkde.tight_layout()
        fkde.savefig(fnamekde)
        plt.close(fkde)

        fjit = plt.figure()
        axjit = fjit.add_subplot(111)
        axjit.scatter(*zip(*v_bef), color='blue', alpha=0.4, s=.5)
        axjit.scatter(*zip(*v_aft), color='green', alpha=0.4, s=.5)
        axjit.set_title("Jitter Plot showing slicewise impact of " + title)
        axjit.set_xlabel('Slice Number')
        axjit.set_ylabel('MSE')
        xlim = tuple((0, nslices + 1))
        ylim = tuple((0, max(np.nanmax(zip(*v_bef)[1]),
                             np.nanmax(zip(*v_aft)[1]))))
        axjit.set_ylim(ylim)
        axjit.set_xlim(xlim)
        axjit.legend(['before, mean = %.2E' % np.mean(zip(*v_bef)[1]),
                     'after, mean = %.2E' % np.mean(zip(*v_aft)[1])])
        fnamejit = qcdir + "/" + fname + "_jitter.png"
        fjit.tight_layout()
        fjit.savefig(fnamejit)
        plt.close(fjit)
        pass

    def opaque_colorscale(self, basemap, reference, alpha=0.5):
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
        opaque_scale = alpha*reference/float(np.nanmax(reference))
        # remaps intensities
        cmap[:,:,3] = opaque_scale
        return cmap

    def expected_variance(self, s, n, qcdir, scanid="", title=""):
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

        fvar = plt.figure()
        axvar = fvar.add_subplot(111)

        axvar.plot(total_var[0:n], '-bD')

        axvar.set_xlabel('Component')
        axvar.set_ylabel('Cumulative Variance')

        axvar.set_title(", ".join([title,"N=", str(n), "Explained Variance=",
                        str(var_acct)]))
        fvar.set_size_inches(6,6)
        fvar.tight_layout()
        fvar.savefig(qcdir + "/" + scanid + "_var.png")
        plt.close(fvar)

    def mask_align(self, mri_data, ref_data, qcdir, scanid="", refid=""):
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
        mgu().execute_cmd(cmd)
        mri_data = mgu().get_braindata(mri_data)
        ref_data = mgu().get_braindata(ref_data)

        # if we have 4d data, np.mean() to get 3d data
        if len(mri_data.shape) == 4:
            mri_data = np.nanmean(mri_data, axis=3)

        falign = plt.figure()

        depth = mri_data.shape[2]

        depth_seq = np.unique(np.round(np.linspace(0, depth - 1, 25)))
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

    def image_align(self, mri_data, ref_data, qcdir, scanid="", refid=""):
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
        mgu().execute_cmd(cmd)
        mri_data = mgu().get_braindata(mri_data)
        ref_data = mgu().get_braindata(ref_data)

        # if we have 4d data, np.mean() to get 3d data
        if len(mri_data.shape) == 4:
            mri_data = np.nanmean(mri_data, axis=3)

        falign = plt.figure()

        depth = mri_data.shape[2]

        depth_seq = np.unique(np.round(np.linspace(0, depth - 1, 25)))
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

    def plot_timeseries(self, timeseries, qcdir=None,
                        scanid=None, refid=None):
        """
        A function to generate a plot of the timeseries
        of the particular ROI. Makes sure nothing nonsensical is
        happening here.

        **Positional Arguments:**
            - timeseries:
                - the timeseries.
            - qcdir:
                - the directory to place quality control figures.
            - scanid:
                - the scan id of the subject.
            - refid:
                - the reference of the atlas we are plotting timeseries
                  for.
        """
        path = qcdir + "/" + scanid + "_" + refid
        fname_ts = path + "_timeseries.png"
        fname_corr = path + "_corr.png"
        fts = plt.figure()
        axts = fts.add_subplot(111)

        axts.plot(timeseries.T)

        axts.set_xlabel("Time Point (TRs)")
        axts.set_ylabel("Intensity")
        axts.set_title(" ".join([scanid, refid, "ROI Timeseries"]))

        fts.set_size_inches(6, 6)
        fts.tight_layout()

        fts.savefig(fname_ts)
        plt.close(fts)

        fcorr = plt.figure()
        axcorr = fcorr.add_subplot(111)

        cax = axcorr.imshow(np.corrcoef(timeseries), interpolation='nearest',
                      cmap=plt.cm.ocean)
        fcorr.colorbar(cax)
        axcorr.set_title(" ".join([scanid, refid,"Correlation Matrix"]))
        axcorr.set_xlabel('ROI')
        axcorr.set_ylabel('ROI')

        fcorr.set_size_inches(6,6)
        fcorr.tight_layout()
        fcorr.savefig(fname_corr)
        plt.close(fcorr)
        pass

    def generate_html_templated(self, location):
        """
        A function for putting the template for html in the correct
        spot.

        **Positional Arguments:**
            - location:
                - the spot you want the html to go.
        """
        cmd = "cp " + os.path.dirname(os.path.realpath(__file__)) +\
            "/templates/qc.html " + location

        mgu().execute_cmd(cmd)
        pass

    def update_template_qc(self, html_qc, dict_keys):
        """
        A function to update an html, using Django-style templated args.

        **Positional Arguments:**
            - html_qc:
                - the path to the html figure to replace kwargs for.
            - dict_keys:
                - a dictionary containing the keys to replace and
                  the values to replace them with.
        """
        template = open(html_qc).read()
        for key, fname in dict_keys.items():
            template = re.sub("{{ " + key + " }}", fname, template)
        qc_html = open(html_qc, "w")
        qc_html.write(template)
        qc_html.close()
        pass
