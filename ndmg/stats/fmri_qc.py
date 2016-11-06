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
from ndmg.stats.qc import qc as mgqc


class fmri_qc(object):

    def __init__(self):
        """
        Enables quality control of fMRI and DTI processing pipelines.
        """
        pass


    def stat_summary(self, mri, mri_raw, mri_mc, mask, voxel,
                     aligned_mprage, atlas, title=None, qcdir=None,
                     scanid=None, qc_html=None):
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
        fmean_ref = plt.figure()
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
        fanat_ref = plt.figure()
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
            # and allow option to add overlap with ref vs mprage
            i = depth_seq[d]
            axmean_ref = fmean_ref.add_subplot(nrows, ncols, d+1)
            axmean_ref.imshow(mgqc().opaque_colorscale(matplotlib.cm.Blues,
                                                     mri_datmean[:, :, i]))
            axmean_ref.imshow(mgqc().opaque_colorscale(matplotlib.cm.Reds,
                                                     at_dat[:, :, i]))
            axmean_ref.set_xlabel('Position (res)')
            axmean_ref.set_ylabel('Position (res)')
            axmean_ref.set_title('%d slice' % i)

            axmean_anat = fmean_anat.add_subplot(nrows, ncols, d+1)
            axmean_anat.imshow(mgqc().opaque_colorscale(matplotlib.cm.Blues,
                                                      mri_datmean[:, :, i]))
            axmean_anat.imshow(mgqc().opaque_colorscale(matplotlib.cm.Reds,
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

            axanat_ref = fanat_ref.add_subplot(nrows, ncols, d+1)
            axanat_ref.imshow(mgqc().opaque_colorscale(matplotlib.cm.Blues,
                                                     mprage_dat[:, :, i]))
            axanat_ref.set_xlabel('Position (res)')
            axanat_ref.set_ylabel('Position (res)')
            axanat_ref.set_title('%d slice' % i)
            axanat_ref.imshow(mgqc().opaque_colorscale(matplotlib.cm.Reds,
                                                     at_dat[:, :, i]))

        for d in range(0, depth):
            axmi.plot(mri_datmi[d, :])

        fname = qcdir + "/"
        axmi.set_xlabel('Timepoint')
        axmi.set_ylabel('Mean Intensity')
        axmi.set_title('Mean Slice Intensity')
        axmi.set_xlim((0, nvols))


        fhist = plt.figure()
        axvih = fhist.add_subplot(111)
        nonzero_data = mri_datmean[mri_datmean != 0]
        hist, bins = np.histogram(nonzero_data, bins=500,
                                 range=(0, np.nanmean(nonzero_data) + 
                                        2*np.nanstd(nonzero_data)))
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / float(2)
        axvih.bar(center, hist, align='center', width=width)
        axvih.set_xlabel('Voxel Intensity')
        axvih.set_ylabel('Number of Voxels')

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

        trans_abs = np.linalg.norm(abs_pos[:, 3:6], axis=1)
        trans_rel = np.linalg.norm(rel_pos[:, 3:6], axis=1)
        rot_abs = np.linalg.norm(abs_pos[:, 0:3], axis=1)
        rot_rel = np.linalg.norm(rel_pos[:, 0:3], axis=1)
        fmc = plt.figure()
        axmc = fmc.add_subplot(111)
        axmc.plot(trans_abs)
        axmc.plot(trans_rel)
        axmc.set_xlabel('Timepoint')
        axmc.set_ylabel('Movement (mm)')
        axmc.set_title('Estimated Displacement')
        axmc.legend(['absolute', 'relative'])
        axmc.set_xlim((0, nvols))

        figures = {"mean_ref": fmean_ref, "mean_anat": fmean_anat,
                   "anat_ref": fanat_ref, "std": fstd, "snr": fsnr,
                    "voxel_hist": fhist, "intens": fmi, "trans": ftrans,
                    "rot": frot, "disp": fmc}
        fnames = {}

        for idx, fig in figures.items():
            fig.tight_layout()
            fig.set_size_inches(nrows*6, ncols*6)
            appended_path = scanid + "_" + str(idx) + ".png"
            fnames[idx] = appended_path
            path = fname + appended_path
            fig.savefig(path)

        
        fnames['sub'] = scanid

        mgqc().update_template_qc(qc_html, fnames)


        fstat = open(fname + scanid + "_stat_sum.txt", 'w')
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
