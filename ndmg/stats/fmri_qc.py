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
from ndmg.stats.alignment_qc import alignment_qc as mgqc
import plotly as py
import plotly.offline as offline


class fmri_qc(object):

    def __init__(self):
        """
        Enables quality control of fMRI and DTI processing pipelines.
        """
        pass

    def stat_summary(self, mri, mri_raw, mri_mc, mask, voxel,
                     aligned_mprage, atlas, title=None, qcdir=None,
                     scanid=None):
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

        axmi_list = []
        for d in range(0, depth):
            axmi_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                                   y=mri_datmi[d, :],
                                                   mode='lines',
                                                   showlegend=False))
        layout = dict(title='Mean Slice Intensity',
                      xaxis=dict(title='Timepoint', range=[0, nvols]),
                      yaxis=dict(title='Mean Intensity'),
                      height=405, width=720)
        axmi = dict(data=axmi_list, layout=layout)
        appended_path = scanid + "_intens.html"
        path = qcdir + "/" + appended_path
        offline.plot(axmi, filename=path, auto_open=False)

        nonzero_data = mri_datmean[mri_datmean != 0]
        hist, bins = np.histogram(nonzero_data, bins=500,
                                  range=(0, np.nanmean(nonzero_data) +
                                         2*np.nanstd(nonzero_data)))
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / float(2)

        axvih = [py.graph_objs.Bar(x=center, y=hist)]
        layout = dict(xaxis=dict(title='Voxel Intensity'),
                      yaxis=dict(title='Number of Voxels'),
                      height=405, width=720)
        fhist = dict(data=axvih, layout=layout)
        appended_path = scanid + "_voxel_hist.html"
        path = qcdir + "/" + appended_path
        offline.plot(fhist, filename=path, auto_open=False)

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

        ftrans_list = []
        ftrans_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                                 y=abs_pos[:, 3],
                                                 mode='lines', name='x'))
        ftrans_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                                 y=abs_pos[:, 4],
                                                 mode='lines', name='y'))
        ftrans_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                                 y=abs_pos[:, 5],
                                                 mode='lines', name='z'))
        layout = dict(title='Translational Motion Parameters',
                      xaxis=dict(title='Timepoint', range=[0, nvols]),
                      yaxis=dict(title='Translation (mm)'))
        ftrans = dict(data=ftrans_list, layout=layout)
        appended_path = scanid + "_trans.html"
        path = qcdir + "/" + appended_path
        offline.plot(ftrans, filename=path, auto_open=False)

        frot_list = []
        frot_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                               y=abs_pos[:, 0],
                                               mode='lines', name='x'))
        frot_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                               y=abs_pos[:, 1],
                                               mode='lines', name='y'))
        frot_list.append(py.graph_objs.Scatter(x=range(0, nvols),
                                               y=abs_pos[:, 2],
                                               mode='lines', name='z'))
        layout = dict(title='Rotational Motion Parameters',
                      xaxis=dict(title='Timepoint', range=[0, nvols]),
                      yaxis=dict(title='Rotation (rad)'))
        frot = dict(data=frot_list, layout=layout)
        appended_path = scanid + "_rot.html"
        path = qcdir + "/" + appended_path
        offline.plot(frot, filename=path, auto_open=False)

        trans_abs = np.linalg.norm(abs_pos[:, 3:6], axis=1)
        trans_rel = np.linalg.norm(rel_pos[:, 3:6], axis=1)
        rot_abs = np.linalg.norm(abs_pos[:, 0:3], axis=1)
        rot_rel = np.linalg.norm(rel_pos[:, 0:3], axis=1)

        fmc_list = []
        fmc_list.append(py.graph_objs.Scatter(x=range(0, nvols), y=trans_abs,
                                              mode='lines', name='absolute'))
        fmc_list.append(py.graph_objs.Scatter(x=range(0, nvols), y=trans_rel,
                                              mode='lines', name='relative'))
        layout = dict(title='Estimated Displacement',
                      xaxis=dict(title='Timepoint', range=[0, nvols]),
                      yaxis=dict(title='Movement (mm)'))
        fmc = dict(data=fmc_list, layout=layout)
        appended_path = scanid + "_disp.html"
        path = qcdir + "/" + appended_path
        offline.plot(fmc, filename=path, auto_open=False)

        figures = {"mean_ref": [fmean_ref, nrows, ncols],
                   "mean_anat": [fmean_anat, nrows, ncols],
                   "anat_ref": [fanat_ref, nrows, ncols],
                   "std": [fstd, nrows, ncols],
                   "snr": [fsnr, nrows, ncols]}
        fnames = {}

        for idx, figlist in figures.items():
            fig = figlist[0]
            fig.set_size_inches(figlist[1]*6, figlist[2]*6)
            fig.tight_layout()
            appended_path = scanid + "_" + str(idx) + ".png"
            fnames[idx] = appended_path
            path = qcdir + "/" + appended_path
            fig.savefig(path)
            plt.close(fig)

        fnames['sub'] = scanid
        fnames['trans'] = scanid + "_trans.html"
        fnames['rot'] = scanid + "_rot.html"
        fnames['disp'] = scanid + "_disp.html"
        fnames['intens'] = scanid + "_intens.html"
        fnames['voxel_hist'] = scanid + "_voxel_hist.html"

        # mgqc().update_template_qc(qc_html, fnames)

        fstat = open(qcdir + "/" + scanid + "_stat_sum.txt", 'w')
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

        absrel = ["absolute", "relative"]
        transrot = ["motion", "rotation"]
        list1 = [max(trans_abs), np.mean(trans_abs), np.sum(trans_abs > 1),
                 np.sum(trans_abs > 5), mean_abs[3], std_abs[3], max_abs[3],
                 mean_abs[4], std_abs[4], max_abs[4], mean_abs[5],
                 std_abs[5], max_abs[5]]
        list2 = [max(trans_rel), np.mean(trans_rel), np.sum(trans_rel > 1),
                 np.sum(trans_rel > 5), mean_abs[3], std_rel[3], max_rel[3],
                 mean_abs[4], std_rel[4], max_rel[4], mean_abs[5],
                 std_rel[5], max_rel[5]]
        list3 = [max(rot_abs), np.mean(rot_abs), 0, 0, mean_abs[0],
                 std_abs[0], max_abs[0], mean_abs[1], std_abs[1],
                 max_abs[1], mean_abs[2], std_abs[2], max_abs[2]]
        list4 = [max(rot_rel), np.mean(rot_rel), 0, 0, mean_rel[0],
                 std_rel[0], max_rel[0], mean_rel[1], std_rel[1],
                 max_rel[1], mean_rel[2], std_rel[2], max_rel[2]]
        lists = [list1, list2, list3, list4]
        headinglist = ["Absolute Translational Statistics>>\n",
                       "Relative Translational Statistics>>\n",
                       "Absolute Rotational Statistics>>\n",
                       "Relative Rotational Statistics>>\n"]
        x = 0
        for motiontype in transrot:
            for measurement in absrel:
                fstat.write(headinglist[x])
                fstat.write("Max " + measurement + " " + motiontype +
                            ": %.4f\n" % lists[x][0])
                fstat.write("Mean " + measurement + " " + motiontype +
                            ": %.4f\n" % lists[x][1])
                if motiontype == "motion":
                    fstat.write("Number of " + measurement + " " + motiontype +
                                "s > 1mm: %.4f\n" % lists[x][2])
                    fstat.write("Number of " + measurement + " " + motiontype +
                                "s > 5mm: %.4f\n" % lists[x][3])
                fstat.write("Mean " + measurement + " x " + motiontype +
                            ": %.4f\n" % lists[x][4])
                fstat.write("Std " + measurement + " x " + motiontype +
                            ": %.4f\n" % lists[x][5])
                fstat.write("Max " + measurement + " x " + motiontype +
                            ": %.4f\n" % lists[x][6])
                fstat.write("Mean " + measurement + " y " + motiontype +
                            ": %.4f\n" % lists[x][7])
                fstat.write("Std " + measurement + " y " + motiontype +
                            ": %.4f\n" % lists[x][8])
                fstat.write("Max " + measurement + " y " + motiontype +
                            ": %.4f\n" % lists[x][9])
                fstat.write("Mean " + measurement + " z " + motiontype +
                            ": %.4f\n" % lists[x][10])
                fstat.write("Std " + measurement + " z " + motiontype +
                            ": %.4f\n" % lists[x][11])
                fstat.write("Max " + measurement + " z " + motiontype +
                            ": %.4f\n" % lists[x][12])
                x = x + 1

        fstat.close()
