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

import nibabel as nb
import sys
import re
import os.path
import matplotlib
import numpy as np
from ndmg.utils import utils as mgu
from ndmg.stats import func_qa_utils as fqc_utils
from ndmg.stats.qa_reg import reg_mri_pngs, plot_brain, plot_overlays
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
        scanid = mgu.get_filename(aligned_func)
        voxel = nb.load(aligned_func).get_data()
        mean_ts = voxel.mean(axis=3)
        std_ts = voxel.std(axis=3)

        np.seterr(divide='ignore', invalid='ignore')
        snr_ts = np.divide(mean_ts, std_ts)

        plots = {}
        plots["mean"] = plot_brain(mean_ts)
        plots["std"] = plot_brain(std_ts)
        plots["snr"] = plot_brain(snr_ts)
        for plotname, plot in plots.iteritems():
            fname = "{}/{}_{}.png".format(qcdir, scanid, plotname)
            plot.savefig(fname, format='png')
            plt.close()
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


    def self_reg_qa(self, saligned_epi, t1w, t1w_brain, sreg_strats, sreg_epis, 
                    sreg_func_dir, sreg_anat_dir, outdir):
        """
        A function that produces self-registration quality control figures.

        **Positional Arguments:**
            - saligned_epi:
                - the self aligned epi sequence.
            - t1w:
                - the anatomical scan associated with the current subject.
            - t1w_brain:
                - the skullstripped brain of the same subject.
            - sreg_strats:
                - the strategies attempted in self registration.
            - sreg_epis:
                - the epi sequences for each step of self registration.
            - sreg_func_dir:
                - the directory to place functional qc images.
            - outdir:
                - the directory where the temporary files will be placed.
        """
        print "Performing QA for Self-Registration..."
        # analyze the quality of each self registration performed
        for (strat, fsreg) in zip(sreg_strats, sreg_epis):
            sc = fqc_utils.registration_score(fsreg, t1w_brain, outdir)
            sreg_f = "{}/{}_score_{:.0f}".format(sreg_func_dir, strat, sc[0]*1000)
            self.reg_func_qa(fsreg, t1w, outdir, sreg_f)
        # make sure to note which brain is actually used
        sreg_f_final = "{}/{}".format(sreg_func_dir, "final")
        sc = fqc_utils.registration_score(saligned_epi, t1w_brain, outdir)
        self.func_reg_sc = sc[0]  # so we can recover this later
        self.reg_func_qa(saligned_epi, t1w, outdir, sreg_f_final)
        # provide qc for the skull stripping step
        t1brain_dat = nb.load(t1w_brain).get_data()
        t1_dat = nb.load(t1w).get_data()
        freg_qual = plot_overlays(t1_dat, t1brain_dat)
        fraw_name = "{}_bet_quality.png".format(mgu.get_filename(t1w_brain))
        fname = "{}/{}".format(sreg_anat_dir, fraw_name)              
        freg_qual.savefig(fname)
        plt.close()
        pass


    def temp_reg_qa(self, aligned_epi, aligned_t1w, atlas, atlas_brain, treg_strats,
                    treg_epis, treg_t1ws, treg_func_dir, treg_anat_dir, outdir):
        """
        A function that produces self-registration quality control figures.
 
        **Positional Arguments:**
           - aligned_epi:
                - the template aligned epi sequence.
            - aligned_t1w:
                - the template aligned  anatomical scan associated
                with the current subject.
            - atlas:
                - the template being aligned to.
            - atlas_brain:
                - the skullstripped brain of the same template.
            - treg_strats:
                - the strategies attempted in self registration.
            - treg_epis:
                - the epi sequences for each step of temp registration.
            - treg_t1ws:
                - the anatomical sequences for each step of temp registration.
            - treg_func_dir:
                - the directory to place functional qc images.
            - treg_anat_dir:
                - the directory to place anatomical qc images.
            - outdir:
                - the directory where the temporary files will be placed.
        """
        print "Performing QA for Template-Registration..."
        # analyze the quality of each self registration performed
        for (strat, ftreg, fareg) in zip(treg_strats, treg_epis, treg_t1ws):
            sc = fqc_utils.registration_score(ftreg, atlas_brain, outdir)
            treg_f = "{}/{}_score_{:.0f}".format(treg_func_dir, strat, sc[0]*1000)
            treg_a = "{}/{}_score_{:.0f}".format(treg_anat_dir, strat, sc[0]*1000)
            self.reg_func_qa(ftreg, atlas, outdir, treg_f)
            self.reg_anat_qa(fareg, atlas, outdir, treg_a)
        # make sure to note which brain is actually used
        treg_f_final = "{}/{}".format(treg_func_dir, "final")
        treg_a_final = "{}/{}".format(treg_anat_dir, "final")
        self.reg_func_qa(aligned_epi, atlas, outdir, treg_a_final)
        self.reg_anat_qa(aligned_t1w, atlas, outdir, treg_a_final)
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
