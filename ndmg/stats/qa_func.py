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

# qa_func.py
# Created by Eric W Bridgeford on 2016-06-08.
# Email: ebridge2@jhu.edu

import nibabel as nb
import sys
import re
import os.path
import matplotlib
import numpy as np
from ndmg.utils import utils as mgu
from ndmg.stats import func_qa_utils as fqc_utils
from ndmg.stats.qa_reg import reg_mri_pngs, plot_brain, plot_overlays
from ndmg.register.register import func_register as ndfr
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly as py
import plotly.offline as offline
import pickle


class qa_func(object):
    def __init__(self):
        pass

    @staticmethod
    def load(filename):
        """
        A function for loading a qa_func object, so that we
        can perform group level quality control easily.

        **Positional Arguments:**
            - filename: the name of the pickle file containing
                our qa_func object
        """
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
        f.close()
        return obj

    def save(self, filename):
        """
        A function for saving a qa_func object.

        **Positional Arguments:**
            - filename: the name of the file we want to save to.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        f.close()
        pass

    def preproc_qa(self, mc_brain, qcdir=None):
        """
        A function for performing quality control given motion
        correction information. Produces plots of the motion correction
        parameters used.

        **Positional Arguments**
            - mc_brain:
                - the motion corrected brain. should have
                an identically named file + '.par' created by mcflirt.
            - scan_id:
                - the id of the subject.
            - qcdir:
                - the quality control directory.
        """
        print "Performing QA for Preprocessing..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        scanid = mgu.get_filename(mc_brain)

        mc_im = nb.load(mc_brain)
        mc_dat = mc_im.get_data()

        mcfig = plot_brain(mc_dat.mean(axis=3))
        nvols = mc_dat.shape[3]

        fnames = {}
        fnames['trans'] = "{}_trans.html".format(scanid)
        fnames['rot'] = "{}_rot.html".format(scanid) 

        par_file = "{}.par".format(mc_brain)
        mc_file = "{}/{}_stats.txt".format(qcdir, scanid)

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

        self.abs_pos = abs_pos
        self.rel_pos = rel_pos

        fmc_list = []
        fmc_list.append(py.graph_objs.Scatter(x=range(0, nvols), y=trans_abs,
                                              mode='lines', name='absolute'))
        fmc_list.append(py.graph_objs.Scatter(x=range(0, nvols), y=trans_rel,
                                              mode='lines', name='relative'))
        layout = dict(title='Estimated Displacement',
                      xaxis=dict(title='Timepoint', range=[0, nvols]),
                      yaxis=dict(title='Movement (mm)'))
        fmc = dict(data=fmc_list, layout=layout)

        disp_path = "{}/{}_disp.html".format(qcdir, scanid)
        offline.plot(fmc, filename=disp_path, auto_open=False)
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
        trans_path = "{}/{}_trans.html".format(qcdir, scanid)
        offline.plot(ftrans, filename=trans_path, auto_open=False)

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
        rot_path ="{}/{}_rot.html".format(qcdir, scanid)
        offline.plot(frot, filename=rot_path, auto_open=False)

        # Motion Statistics
        mean_abs = np.mean(abs_pos, axis=0)  # column wise means per param
        std_abs = np.std(abs_pos, axis=0)
        max_abs = np.max(np.abs(abs_pos), axis=0)
        mean_rel = np.mean(rel_pos, axis=0)
        std_rel = np.std(rel_pos, axis=0)
        max_rel = np.max(np.abs(rel_pos), axis=0)

        fstat = open(mc_file, 'w')
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
        return


    def reg_func_qa(self, aligned_func, atlas, outdir, qcdir):
        """
        A function that produces quality control information for registration
        leg of the pipeline for functional scans.

        **Positional Arguments**
            - aligned_func:
                - the aligned functional MRI.
            - atlas:
                - the atlas the functional brain is aligned to.
            - outdir:
                - the directory where temporary files will be placed.
            - qcdir:
                - the directory in which quality control images will
                be placed.
        """
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        reg_mri_pngs(aligned_func, atlas, qcdir, mean=True)
        pass


    def reg_anat_qa(self, aligned_anat, atlas, outdir, qcdir):
        """
        A function that produces quality control information for registration
        leg of the pipeline for anatomical scans.

        **Positional Arguments**
            - aligned_anat:
                - the aligned anatomical MRI.
            - atlas:
                - the atlas the functional and anatomical brains
                were aligned to.
            - outdir:
                - the directory where temporary files will be placed.
            - qcdir:
                - the directory in which quality control images will
                be placed.
        """
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        anat_name = mgu.get_filename(aligned_anat)
        anat_brain = mgu.name_tmps(outdir, anat_name, "_brain.nii.gz")
        # extract brain and use generous 0.3 threshold
        mgu.extract_brain(aligned_anat, anat_brain, opts=' -f 0.3 -B -R -S')

        reg_mri_pngs(anat_brain, atlas, qcdir)
        return


    def self_reg_qa(self, freg, sreg_func_dir, sreg_anat_dir, outdir):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**
            - freg:
                - the func_register object from registration.
            - sreg_func_dir:
                - the directory to place functional qc images.
            - outdir:
                - the directory where the temporary files will be placed.
        """
        print "Performing QA for Self-Registration..."
        # analyze the quality of each self registration performed
        regiter = zip(freg.sreg_strat, freg.sreg_epi,
                      freg.sreg_sc, freg.sreg_sc_fig)
        for (strat, fsreg, sc, fig_ov) in regiter:
            sreg_f = "{}/{}_score_{:.0f}".format(sreg_func_dir, strat, sc*1000)
            func_name = mgu.get_filename(fsreg)
            self.reg_func_qa(fsreg, freg.t1w, outdir, sreg_f)
            fname = "{}/{}_bet_quality.png".format(sreg_f, func_name)
            fig_ov.savefig(fname)
            plt.close()
        # make sure to note which brain is actually used
        best_sc = np.max(freg.sreg_sc)
        sreg_f_final = "{}/{}_score_{:.0f}".format(sreg_func_dir, "final", sc*1000)
        self.self_reg_sc = best_sc  # so we can recover this later
        self.reg_func_qa(freg.saligned_epi, freg.t1w, outdir, sreg_f_final)
        # provide qc for the skull stripping step
        t1brain_dat = nb.load(freg.t1w_brain).get_data()
        t1_dat = nb.load(freg.t1w).get_data()
        freg_qual = plot_overlays(t1_dat, t1brain_dat)
        fraw_name = "{}_bet_quality.png".format(mgu.get_filename(freg.t1w_brain))
        fname = "{}/{}".format(sreg_anat_dir, fraw_name)              
        freg_qual.savefig(fname)
        plt.close()
        pass


    def temp_reg_qa(self, freg, treg_func_dir, treg_anat_dir, outdir):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**
            - freg:
                - the functional registration object.
            - treg_func_dir:
                - the directory to place functional qc images.
            - treg_anat_dir:
                - the directory to place anatomical qc images.
            - outdir:
                - the directory where the temporary files will be placed.
        """
        print "Performing QA for Template-Registration..."
        # analyze the quality of each self registration performed
        regiter =  zip(freg.treg_strat, freg.treg_epi, freg.treg_t1w,
                       freg.treg_sc, freg.treg_sc_fig)
        for (strat, ftreg, fareg, sc, fig_ov) in regiter:
            treg_f = "{}/{}_score_{:.0f}".format(treg_func_dir, strat, sc*1000)
            treg_a = "{}/{}_score_{:.0f}".format(treg_anat_dir, strat, sc*1000)
            self.reg_func_qa(ftreg, freg.atlas, outdir, treg_f)
            self.reg_anat_qa(fareg, freg.atlas, outdir, treg_a)
            func_name = mgu.get_filename(ftreg)
            fname = "{}/{}_bet_quality.png".format(treg_f, func_name)
            fig_ov.savefig(fname)
            plt.close()
        # make sure to note which brain is actually used
        best_sc = np.max(freg.treg_sc)
        treg_f_final = "{}/{}_score_{:.0f}".format(treg_func_dir, "final", best_sc*1000)
        treg_a_final = "{}/{}_score_{:.0f}".format(treg_anat_dir, "final", best_sc*1000)
        self.temp_reg_sc = best_sc  # so we can recover this later 
        self.reg_func_qa(freg.taligned_epi, freg.atlas, outdir, treg_f_final)
        self.reg_anat_qa(freg.taligned_t1w, freg.atlas, outdir, treg_a_final)

        # estimating mean signal intensity and deviation in brain/non-brain
        fmri = nb.load(freg.taligned_epi)
        mask = nb.load(freg.atlas_mask)
        fmri_dat = fmri.get_data()
        mask_dat = mask.get_data()

        # threshold to identify the brain and non-brain regions
        brain = fmri_dat[mask_dat > 0, :]
        non_brain = fmri_dat[mask_dat == 0, :]
        # identify key statistics
        mean_brain = brain.mean()
        std_nonbrain = np.nanstd(non_brain)
        std_brain = np.nanstd(brain)
        self.snr = mean_brain/std_nonbrain
        self.cnr = std_brain/std_nonbrain

        scanid = mgu.get_filename(freg.taligned_epi)

        np.seterr(divide='ignore', invalid='ignore')
        mean_ts = fmri_dat.mean(axis=3)
        snr_ts = np.divide(mean_ts, std_nonbrain)
        cnr_ts = np.divide(np.nanstd(fmri_dat, axis=3), std_nonbrain)

        plots = {}
        plots["mean"] = plot_brain(mean_ts)
        plots["snr"] = plot_brain(snr_ts)
        plots["cnr"] = plot_brain(cnr_ts)
        for plotname, plot in plots.iteritems():
            fname = "{}/{}_{}.png".format(treg_f_final, scanid, plotname)
            plot.savefig(fname, format='png')
            plt.close()
        pass


    def nuisance_qa(self, nuis_ts, nuis_brain, prenuis_brain, qcdir=None):
        """
        A function to assess the quality of nuisance correction.

        **Positional Arguments**
            - nuis_brain:
                - the nuisance corrected brain image.
            - prenuis_brain:
                - the brain before nuisance correction.
            - qcdir:
                - the directory to place quality control images.
        """
        print "Performing QA for Nuisance..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
        return

    def roi_ts_qa(self, timeseries, func, anat, label, qcdir=None):
        """
        A function to perform ROI timeseries quality control.

        **Positional Arguments**
            - timeseries:
                - a path to the ROI timeseries.
            - func:
                - the functional image that has timeseries
                extract from it.
            - anat:
                - the anatomical image that is aligned.
            - label:
                - the label in which voxel timeseries will be
                downsampled.
            - qcdir:
                - the quality control directory to place outputs.
        """
        print "Performing QA for ROI Timeseries..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
     
        reg_mri_pngs(anat, label, qcdir)
        fqc_utils.plot_timeseries(timeseries, qcdir=qcdir)
        return

    def voxel_ts_qa(self, timeseries, voxel_func, atlas_mask, qcdir=None):
        """
        A function to analyze the voxel timeseries extracted.

        **Positional Arguments**
            - voxel_func:
                - the functional timeseries that
              has voxel timeseries extracted from it.
            - atlas_mask:
                - the mask under which
              voxel timeseries was extracted.
            - qcdir:
                - the directory to place qc in.
        """
        print "Performing QA for Voxel Timeseries..."
        cmd = "mkdir -p {}".format(qcdir)
        mgu.execute_cmd(cmd)
     
        reg_mri_pngs(voxel_func, atlas_mask, qcdir, loc=0)
        return
