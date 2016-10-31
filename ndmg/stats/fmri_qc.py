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

# fmri_qc.py
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


class fmri_qc(object):

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
            from ndmg.register import register as mgr
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
        pass

    def opaque_colorscale(self, basemap, reference):
        """
        A function to return a colorscale, with opacities
        dependent on reference intensities.

        **Positional Arguments:**
            reference:
                - the reference matrix.
        """
        cmap = basemap(reference)
        # all values beteween 0 opacity and .6
        opaque_scale = 0.5*reference/float(np.nanmax(reference))
        # remaps intensities
        cmap[:,:,3] = opaque_scale
        return cmap

    def image_align(self, mri_data, ref_data, qcdir, scanid="", refid="",
                    binmri=False, binref=False):
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
            binmri:
                - determines whether binarization will take place
                for mri image.
            binref:
                - determines whether binarization will take place for
                reference
        """
        cmd = "mkdir -p " + qcdir
        mgu().execute_cmd(cmd)
        mri_data = mgu().get_brain(mri_data)
        ref_data = mgu().get_brain(ref_data)

        # if we have 4d data, np.mean() to get 3d data
        if len(mri_data.shape) == 4:
            mri_data = np.nanmean(mri_data, axis=3)

        if binmri is True:
            mri_data = (mri_data != 0).astype(float)

        if binref is True:
            ref_data = (ref_data != 0).astype(float)

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
        falign.savefig(qcdir + "/" + scanid + "_" + refid + "_overlap.png")

    def stat_summary(self, mri, mri_raw, mri_mc, mask, voxel,
                     aligned_mprage, atlas, title="", qcdir="",
                     scanid=""):
        """
        A function for producing a stat summary page, along with
        an image of all the slices of this mri scan.

        **Outputs:**
            Mean figure:
                - plot for each voxel's mean signal intensity for
              each voxel in the corrected mri's timecourse
            STdev figure:
                - plot of the standard deviation of each voxel's
              corrected timecourse
            SNR figure:
                - plot of signal to noise ratio for each voxel in the
              corrected timecourse
            Slice Wise Intensity figure:
                - averages intensity over slices
                    and plots each slice as a line for corrected mri
                - goal: slice mean signal intensity is approximately same
                  throughout all nvols (lines are relatively flat)
            motion parameters figures (3):
                - 1 figure for rotational, 1 figure for translational motion
                  params, 1 for displacement, calculated with fsl's mcflirt
            stat summary file:
                - provides some useful statistics for analyzing fMRI data;
                  see resources for each individual statistic for the
                  computation

        **Positional Arguments:**
            - mri:
                - the path to a corrected mri scan to analyze
            - mri_raw:
                - the path to an uncorrected mri scan to analyze
            - mri_mc:
                - the motion corrected mri scan.
            - mask:
                - the mask to calculate statistics over.
            - voxel:
                - a matrix for the voxel timeseries.
            - aligned_mprage:
                - the aligned MPRAGE image.
            - atlas:
                - the atlas for alignment.
            - title:
                - the title for the plots (ie, Registered, Resampled, etc)
            - fname:
                - the name to give the file.
        """
        print "Producing Quality Control Summary. \n" +\
            "\tRaw Image: " + mri_raw + "\n" +\
            "\tCorrected Image: " + mri + "\n" +\
            " \tMask: " + mask + "\n"
        cmd = "mkdir -p " + qcdir
        mgu().execute_cmd(cmd)

        mri_im = nb.load(mri)
        mri_dat = mri_im.get_data()
        mri_raw_im = nb.load(mri_raw)

        mprage_dat = nb.load(aligned_mprage).get_data()
        at_dat = nb.load(atlas).get_data()

        print "Opened MRI Images."

        # image for mean signal intensity over time
        mri_datmean = np.nanmean(mri_dat, axis=3)
        fmean_mni = plt.figure()
        fmean_anat = plt.figure()

        mri_datstd = np.nanstd(mri_dat, axis=3)
        fstd = plt.figure()

        # image for slice SNR = mean / stdev
        mri_datsnr = np.divide(mri_datmean, mri_datstd)
        mri_datsnr[np.isnan(mri_datsnr)] = 0
        fsnr = plt.figure()

        # image for slice-wise mean intensity
        mri_datmi = np.squeeze(np.apply_over_axes(np.nanmean,
                                                  mri_dat, (0, 1)))
        fanat_mni = plt.figure()
        fmi = plt.figure()
        axmi = fmi.add_subplot(111)

        depth = mri_dat.shape[2]
        nvols = mri_dat.shape[3]

        # max image size is 5x5. after that, reduce size to 5x5
        # with sequences
        depth_seq = np.unique(np.round(np.linspace(0, depth - 1, 25)))
        nrows = np.ceil(np.sqrt(depth_seq.shape[0]))
        ncols = np.ceil(depth_seq.shape[0]/float(nrows))

        mri_dat = None  # done with this, so save memory here

        # produce figures for each slice in the image
        for d in range(0, depth_seq.shape[0]):
            # TODO EB: create nifti image with these values
            # and allow option to add overlap with mni vs mprage
            i = depth_seq[d]
            axmean_mni = fmean_mni.add_subplot(nrows, ncols, d+1)
            axmean_mni.imshow(self.opaque_colorscale(matplotlib.cm.Blues,
                                                     mri_datmean[:, :, i]))
            axmean_mni.imshow(self.opaque_colorscale(matplotlib.cm.Reds,
                                                     at_dat[:, :, i]))
            axmean_mni.set_xlabel('Position (res)')
            axmean_mni.set_ylabel('Position (res)')
            axmean_mni.set_title('%d slice' % i)

            axmean_anat = fmean_anat.add_subplot(nrows, ncols, d+1)
            axmean_anat.imshow(self.opaque_colorscale(matplotlib.cm.Blues,
                                                      mri_datmean[:, :, i]))
            axmean_anat.imshow(self.opaque_colorscale(matplotlib.cm.Reds,
                                                      mprage_dat[:, :, i]))
            axmean_anat.set_xlabel('Position (res)')
            axmean_anat.set_ylabel('Position (res)')
            axmean_anat.set_title('%d slice' % i)

            axstd = fstd.add_subplot(nrows, ncols, d+1)
            axstd.imshow(mri_datstd[:, :, i], cmap='gray',
                         interpolation='nearest', vmin=0,
                         vmax=np.max(mri_datstd))
            axstd.set_xlabel('Position (res)')
            axstd.set_ylabel('Position (res)')
            axstd.set_title('%d slice' % i)

            axsnr = fsnr.add_subplot(nrows, ncols, d+1)
            axsnr.imshow(mri_datsnr[:, :, i], cmap='gray',
                         interpolation='nearest', vmin=0,
                         vmax=np.max(mri_datsnr))
            axsnr.set_xlabel('Position (res)')
            axsnr.set_ylabel('Position (res)')
            axsnr.set_title('%d slice' % i)

            axanat_mni = fanat_mni.add_subplot(nrows, ncols, d+1)
            axanat_mni.imshow(self.opaque_colorscale(matplotlib.cm.Blues,
                                                     mprage_dat[:, :, i]))
            axanat_mni.set_xlabel('Position (res)')
            axanat_mni.set_ylabel('Position (res)')
            axanat_mni.set_title('%d slice' % i)
            axanat_mni.imshow(self.opaque_colorscale(matplotlib.cm.Reds,
                                                     at_dat[:, :, i]))

        for d in range(0, depth):
            axmi.plot(mri_datmi[d, :])

        fname = qcdir + "/" + scanid
        axmi.set_xlabel('Timepoint')
        axmi.set_ylabel('Mean Intensity')
        axmi.set_title('Mean Slice Intensity')
        axmi.set_xlim((0, nvols))
        fmean_mni.set_size_inches(nrows*6, ncols*6)
        fmean_anat.set_size_inches(nrows*6, ncols*6)
        fstd.set_size_inches(nrows*6, ncols*6)
        fsnr.set_size_inches(nrows*6, ncols*6)
        fanat_mni.set_size_inches(nrows*6, ncols*6)

        fmean_mni.tight_layout()
        fmean_mni.savefig(fname + "_mean_mni.png")
        fmean_anat.tight_layout()
        fmean_anat.savefig(fname + "_mean_anat.png")
        fstd.tight_layout()
        fstd.savefig(fname + "_std.png")
        fsnr.tight_layout()
        fsnr.savefig(fname + "_snr.png")
        fmi.tight_layout()
        fmi.savefig(fname + "_slice_intens.png")
        fanat_mni.tight_layout()
        fanat_mni.savefig(fname + "_anat_mni.png")

        fvoxel_intens_hist = plt.figure()
        axvih = fvoxel_intens_hist.add_subplot(111)
        nonzero_data = mri_datmean[mri_datmean != 0]
        hist, bins = np.histogram(nonzero_data, bins=500,
                                 range=(0, np.nanmean(nonzero_data) + 
                                        2*np.nanstd(nonzero_data)))
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / float(2)
        axvih.bar(center, hist, align='center', width=width)
        axvih.set_xlabel('Voxel Intensity')
        axvih.set_ylabel('Number of Voxels')
        fvoxel_intens_hist.tight_layout() 
        fvoxel_intens_hist.savefig(fname + "_hist.png")

        par_file = mri_mc + ".par"

        abs_pos = np.zeros((nvols, 6))
        rel_pos = np.zeros((nvols, 6))
        with open(par_file) as f:
            counter = 0
            for line in f:
                abs_pos[counter, :] = [float(i) for i in re.split("\\s+",
                                                                  line)[0:6]]
                if counter > 0:
                    rel_pos[counter, :] = np.subtract(abs_pos[counter, :],
                                                      abs_pos[counter-1, :])
                counter += 1

        trans_abs = np.linalg.norm(abs_pos[:, 3:6], axis=1)
        trans_rel = np.linalg.norm(rel_pos[:, 3:6], axis=1)
        rot_abs = np.linalg.norm(abs_pos[:, 0:3], axis=1)
        rot_rel = np.linalg.norm(rel_pos[:, 0:3], axis=1)

        ftrans = plt.figure()
        axtrans = ftrans.add_subplot(111)
        axtrans.plot(abs_pos[:, 3:6])  # plots the parameters
        axtrans.set_xlabel('Timepoint')
        axtrans.set_ylabel('Translation (mm)')
        axtrans.set_title('Translational Motion Parameters')
        axtrans.legend(['x', 'y', 'z'])
        axtrans.set_xlim((0, nvols))
        ftrans.tight_layout()
        ftrans.savefig(fname + "_trans_mc.png")

        frot = plt.figure()
        axrot = frot.add_subplot(111)
        axrot.plot(abs_pos[:, 0:3])
        axrot.set_xlabel('Timepoint')
        axrot.set_ylabel('Rotation (rad)')
        axrot.set_title('Rotational Motion Parameters')
        axrot.legend(['x', 'y', 'z'])
        axrot.set_xlim((0, nvols))
        frot.tight_layout()
        frot.savefig(fname + "_rot_mc.png")

        fmc = plt.figure()
        axmc = fmc.add_subplot(111)
        axmc.plot(trans_abs)
        axmc.plot(trans_rel)
        axmc.set_xlabel('Timepoint')
        axmc.set_ylabel('Movement (mm)')
        axmc.set_title('Estimated Displacement')
        axmc.legend(['absolute', 'relative'])
        axmc.set_xlim((0, nvols))
        fmc.tight_layout()
        fmc.savefig(fname + "_disp_mc.png")

        fstat = open(fname + "_stat_sum.txt", 'w')
        fstat.write("General Information\n")
        fstat.write("Raw Image Resolution: " +
                    str(mri_raw_im.get_header().get_zooms()[0:3]) + "\n")
        fstat.write("Corrected Image Resolution: " +
                    str(mri_im.get_header().get_zooms()[0:3]) + "\n")
        fstat.write("Number of Volumes: %d" % nvols)

        fstat.write("\n\n")
        fstat.write("Signal  Statistics\n")
        fstat.write("Signal Mean: %.4f\n" % np.mean(voxel))
        fstat.write("Signal Stdev: %.4f\n" % np.std(voxel))
        fstat.write("Number of Voxels: %d\n" % voxel.shape[0])
        fstat.write("Average SNR per voxel: %.4f\n" %
                    np.nanmean(np.divide(np.mean(voxel, axis=1),
                               np.std(voxel, axis=1))))
        fstat.write("\n\n")

        # Motion Statistics
        mean_abs = np.mean(abs_pos, axis=0)  # column wise means per param
        std_abs = np.std(abs_pos, axis=0)
        max_abs = np.max(np.abs(abs_pos), axis=0)
        mean_rel = np.mean(rel_pos, axis=0)
        std_rel = np.std(rel_pos, axis=0)
        max_rel = np.max(np.abs(rel_pos), axis=0)
        fstat.write("Motion Statistics\n")
        fstat.write("Absolute Translational Statistics>>\n")
        fstat.write("Max absolute motion: %.4f\n" % max(trans_abs))
        fstat.write("Mean absolute motion: %.4f\n" % np.mean(trans_abs))
        fstat.write("Number of absolute motions > 1mm: %d\n" %
                    np.sum(trans_abs > 1))
        fstat.write("Number of absolute motions > 5mm: %d\n" %
                    np.sum(trans_abs > 5))
        fstat.write("Mean absolute x motion: %.4f\n" %
                    mean_abs[3])
        fstat.write("Std absolute x position: %.4f\n" %
                    std_abs[3])
        fstat.write("Max absolute x motion: %.4f\n" %
                    max_abs[3])
        fstat.write("Mean absolute y motion: %.4f\n" %
                    mean_abs[4])
        fstat.write("Std absolute y position: %.4f\n" %
                    std_abs[4])
        fstat.write("Max absolute y motion: %.4f\n" %
                    max_abs[4])
        fstat.write("Mean absolute z motion: %.4f\n" %
                    mean_abs[5])
        fstat.write("Std absolute z position: %.4f\n" %
                    std_abs[5])
        fstat.write("Max absolute z motion: %.4f\n" %
                    max_abs[5])

        fstat.write("Relative Translational Statistics>>\n")
        fstat.write("Max relative motion: %.4f\n" % max(trans_rel))
        fstat.write("Mean relative motion: %.4f\n" % np.mean(trans_rel))
        fstat.write("Number of relative motions > 1mm: %d\n" %
                    np.sum(trans_rel > 1))
        fstat.write("Number of relative motions > 5mm: %d\n" %
                    np.sum(trans_rel > 5))
        fstat.write("Mean relative x motion: %.4f\n" %
                    mean_abs[3])
        fstat.write("Std relative x motion: %.4f\n" %
                    std_rel[3])
        fstat.write("Max relative x motion: %.4f\n" %
                    max_rel[3])
        fstat.write("Mean relative y motion: %.4f\n" %
                    mean_abs[4])
        fstat.write("Std relative y motion: %.4f\n" %
                    std_rel[4])
        fstat.write("Max relative y motion: %.4f\n" %
                    max_rel[4])
        fstat.write("Mean relative z motion: %.4f\n" %
                    mean_abs[5])
        fstat.write("Std relative z motion: %.4f\n" %
                    std_rel[5])
        fstat.write("Max relative z motion: %.4f\n" %
                    max_rel[5])

        fstat.write("Absolute Rotational Statistics>>\n")
        fstat.write("Max absolute rotation: %.4f\n" % max(rot_abs))
        fstat.write("Mean absolute rotation: %.4f\n" % np.mean(rot_abs))
        fstat.write("Mean absolute x rotation: %.4f\n" %
                    mean_abs[0])
        fstat.write("Std absolute x rotation: %.4f\n" %
                    std_abs[0])
        fstat.write("Max absolute x rotation: %.4f\n" %
                    max_abs[0])
        fstat.write("Mean absolute y rotation: %.4f\n" %
                    mean_abs[1])
        fstat.write("Std absolute y rotation: %.4f\n" %
                    std_abs[1])
        fstat.write("Max absolute y rotation: %.4f\n" %
                    max_abs[1])
        fstat.write("Mean absolute z rotation: %.4f\n" %
                    mean_abs[2])
        fstat.write("Std absolute z rotation: %.4f\n" %
                    std_abs[2])
        fstat.write("Max absolute z rotation: %.4f\n" %
                    max_abs[2])

        fstat.write("Relative Rotational Statistics>>\n")
        fstat.write("Max relative rotation: %.4f\n" % max(rot_rel))
        fstat.write("Mean relative rotation: %.4f\n" % np.mean(rot_rel))
        fstat.write("Mean relative x rotation: %.4f\n" %
                    mean_rel[0])
        fstat.write("Std relative x rotation: %.4f\n" %
                    std_rel[0])
        fstat.write("Max relative x rotation: %.4f\n" %
                    max_rel[0])
        fstat.write("Mean relative y rotation: %.4f\n" %
                    mean_rel[1])
        fstat.write("Std relative y rotation: %.4f\n" %
                    std_rel[1])
        fstat.write("Max relative y rotation: %.4f\n" %
                    max_rel[1])
        fstat.write("Mean relative z rotation: %.4f\n" %
                    mean_rel[2])
        fstat.write("Std relative z rotation: %.4f\n" %
                    std_rel[2])
        fstat.write("Max relative z rotation: %.4f\n" %
                    max_rel[2])

        fstat.close()
        pass

    def make_html_qc(self, sub, qcdir):
        """
        A function for making templated html quality control summary.

        **Positional Arguments:**
            - sub:
                 - the subject.
            - qcdir:
                 - the root quality control directory.
        """

        template = open(os.path.dirname(__file__) + '/templates/qc.html', 'r').read()
        context = {
            'sub': sub,
            'qcdir': qcdir
        }
        for key in context:
            template = re.sub("{{ " + key + " }}", context[key], template)

        qc_html = open(qcdir + "/overall/" + sub + "/" + sub + "_qc.html", "w")
        qc_html.write(template)
        qc_html.close()
        pass
