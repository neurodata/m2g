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

# group_func.py
# Created by Eric W Bridgeford on 2016-04-03.
# Email: ebridge2@jhu.edu

import pickle
import plotly as py
import plotly.offline as pyo
from plotly.tools import make_subplots
from plotly.tools import FigureFactory as ff
from ndmg.stats.qa_func import qa_func as fqa
import numpy as np
import ndmg.utils as mgu
import os
import pandas as pd


class group_func(object):
    def __init__(self, basedir, outdir, dataset=None):
        """
        A class for group level quality control.

        **Positional Arguments:**
            - basedir:
                - the ndmg-formatted functional outputs.
                  should have a qa/ folder contained within it.
            - outdir:
                - the directory to place all group level quality control.
            - dataset:
                - an optional parameter for the name of the dataset
                  to be present in the quality control output filenames.
        """
        self.ndmgdir = basedir
        self.qadir = "{}/qa".format(self.ndmgdir)
        self.outdir = outdir
        self.conn_dir = "{}/connectomes".format(self.ndmgdir)
        self.dataset = dataset

        (self.qa_files, self.subs) = self.get_qa_files()
        self.connectomes = self.get_connectomes()
        self.qa_objects = self.load_qa()
        self.group_level_analysis()
        self.connectome_analysis()
        pass

    def get_qa_files(self):
        """
        A function to load the relevant quality assessment files,
        for all the subjects we have in our study, given a properly-formatted
        ndmg functional directory.
        """
        qa_files = []
        subs = []
        for sub in os.listdir(self.qadir):
            sub_qa = "{}/{}/{}_stats.pkl".format(self.qadir, sub, sub)
            # if the files exists, add it to our qa_files
            if os.path.isfile(sub_qa):
                qa_files.append(sub_qa)
                subs.append(sub)
        return (qa_files, subs)

    def get_connectomes(self):
        """
        A function to load the relevant connectomes for all of the subjects
        for each parcellation we have.
        """
        connectomes = {}
        for label in os.listdir(self.conn_dir):
            this_label = []
            label_dir = "{}/{}/".format(self.conn_dir, label)
            for connectome in os.listdir(dataset_dir):
                if os.path.isfile(connectome):
                    this_label.append(connectome)
            connectomes[label] = this_label
        return connectomes

    def load_qa(self):
        """
        A function to load the quality control objects.
        """
        qa_objects = []
        for qa_file in self.qa_files:
            # load the qa objects as qa_func objects
            qa_objects.append(fqa.load(qa_file))
        return qa_objects

    def group_level_analysis(self):
        """
        A function to perform group level analysis after loading the
        functional qa objects properly.
        """
        self.group_reg()
        self.group_motion()

    def group_reg(self):
        """
        A function that performs group level registration quality control.
        """
        regdir = "{}/{}".format(self.outdir, "reg")
        cmd = "mkdir -p {}".format(regdir)
        mgu.execute_cmd(cmd)

        self_reg_sc = []
        temp_reg_sc = []
        cnr = []
        snr = []
        for sub in self.qa_objects:
            self_reg_sc.append(sub.self_reg_sc)
            temp_reg_sc.append(sub.temp_reg_sc)
            cnr.append(sub.cnr)
            snr.append(sub.snr)

        # need to use pandas to make the violin plots look right
        sreg_sc_names = ['Self']*len(self_reg_sc)
        sreg_sc_df = pd.DataFrame(dict(Score=self_reg_sc,
                                      Method=sreg_sc_names))
        treg_sc_names = ['Template']*len(temp_reg_sc)
        treg_sc_df = pd.DataFrame(dict(Score=temp_reg_sc,
                                      Method=treg_sc_names))
        cnr_names = ['CNR']*len(cnr)
        cnr_df = pd.DataFrame(dict(CNR=cnr, ratio=cnr_names))
        snr_names = ['SNR']*len(snr)
        snr_df = pd.DataFrame(dict(SNR=snr, ratio=snr_names))

        fig_sreg_sc = ff.create_violin(sreg_sc_df, data_header='Score',
                                    group_header='Method',
                                    title='Self Registration Scores')
        fig_treg_sc = ff.create_violin(treg_sc_df, data_header='Score',
                                    group_header='Method',
                                    title='Template Registration Scores')
        fig_cnr = ff.create_violin(cnr_df, data_header='CNR',
                                   group_header='ratio',
                                   title='Contrast to Noise Ratio')
        fig_snr = ff.create_violin(snr_df, data_header='SNR',
                                   group_header='ratio',
                                   title='Signal to Noise Ratio')

        #fig_reg = make_subplots(rows=2, cols=2)
        #fig_reg.append_trace(fig_sreg_sc, 1, 1)
        #fig_reg.append_trace(fig_treg_sc, 1, 2)
        #fig_reg.append_trace(fig_cnr, 2, 1)
        #fig_reg.append_trace(fig_snr, 2, 2)
        

        #fname_reg_sc = "self_reg_scores.html"
        fname_sreg_sc = "self_sreg_scores.html"
        fname_treg_sc = "self_treg_scores.html"
        fname_cnr = "cnr_reg_group.html"
        fname_snr = "snr_reg_group.html"
        # if a dataset name is provided, add it to the name
        if self.dataset is not None:
            #fname_reg_sc = "{}_{}".format(self.dataset,
            #                               fname_reg_sc)
            fname_sreg_sc = "{}_{}".format(self.dataset,
                                           fname_sreg_sc)
            fname_treg_sc = "{}_{}".format(self.dataset,
                                           fname_treg_sc)
            fname_cnr = "{}_{}".format(self.dataset,
                                          fname_cnr)
            fname_snr = "{}_{}".format(self.dataset,
                                          fname_snr)

        fname_sreg_sc = "{}/{}".format(regdir, fname_sreg_sc)
        fname_treg_sc = "{}/{}".format(regdir, fname_treg_sc)
        #fname_reg_sc = "{}/{}".format(regdir, fname_reg_sc)
        fname_cnr = "{}/{}".format(regdir, fname_cnr)
        fname_snr = "{}/{}".format(regdir, fname_snr)

        pyo.plot(fig_snr, filename=fname_snr, auto_open=False)
        pyo.plot(fig_sreg_sc, filename=fname_sreg_sc, auto_open=False)
        pyo.plot(fig_treg_sc, filename=fname_treg_sc, auto_open=False)
        #pyo.plot(fig_reg, filename=fname_reg_sc, auto_open=False)
        pyo.plot(fig_cnr, filename=fname_cnr, auto_open=False)
        pass

    def group_motion(self):
        """
        A function that performs group level motion corrective quality control.
        """
        mcdir = "{}/{}".format(self.outdir, "mc")
        cmd = "mkdir -p {}".format(mcdir)
        mgu.execute_cmd(cmd)

        trans_abs = np.zeros((len(self.qa_objects)))
        trans_rel = np.zeros((len(self.qa_objects)))
        trans_abs_gt = np.zeros((len(self.qa_objects)))
        trans_rel_gt = np.zeros((len(self.qa_objects)))

        for i, sub in enumerate(self.qa_objects):
            abs_m = np.linalg.norm(sub.abs_pos[:, 3:6], axis=1)
            rel_m = np.linalg.norm(sub.rel_pos[:, 3:6], axis=1)
            trans_abs[i] = np.mean(abs_m)
            trans_rel[i] = np.mean(rel_m)
            trans_abs_gt[i] = np.sum(abs_m > 0.2)
            trans_rel_gt[i] = np.sum(rel_m > 0.05)

        fname_abs = "trans_absolute_group.html"
        fname_rel = "trans_relative_group.html"
        fname_abs_gt = "large_trans_absolute_motion.html"
        fname_rel_gt = "large_trans_relative_motion.html"

        # if a dataset name is provided, add it to the name
        if self.dataset is not None:
            fname_abs = "{}_{}".format(self.dataset,
                                          fname_abs)
            fname_rel = "{}_{}".format(self.dataset,
                                          fname_rel)
            fname_abs_gt = "{}_{}".format(self.dataset,
                                          fname_abs_gt)
            fname_rel_gt = "{}_{}".format(self.dataset,
                                          fname_rel_gt)
        fname_abs = "{}/{}".format(mcdir, fname_abs)
        fname_rel = "{}/{}".format(mcdir, fname_rel)
        fname_abs_gt = "{}/{}".format(mcdir, fname_abs_gt)
        fname_rel_gt = "{}/{}".format(mcdir, fname_rel_gt)
 
        abs_mc_names = ['absolute']*len(trans_abs)
        abs_df = pd.DataFrame(dict(motion=trans_abs.tolist(), mtype=abs_mc_names))
        rel_mc_names =['relative']*len(trans_rel)
        rel_df = pd.DataFrame(dict(motion=trans_rel.tolist(), mtype=rel_mc_names))
        abs_gt_names = ['absolute']*len(trans_abs_gt)
        abs_gt_df = pd.DataFrame(dict(number=trans_abs_gt.tolist(), mtype=abs_gt_names))
        rel_gt_names = ['relative']*len(trans_rel_gt)
        rel_gt_df = pd.DataFrame(dict(number=trans_rel_gt.tolist(), mtype=rel_gt_names)) 

        fig_abs = ff.create_violin(abs_df, data_header='motion',
                                    group_header='mtype',
                                    title='Average Absolute Translational Motion (mm)')
 
        fig_rel = ff.create_violin(rel_df, data_header='motion',
                                   group_header='mtype',
                                   title='Average Relative Translational Motion (mm)')
        fig_abs_gt = ff.create_violin(abs_gt_df, data_header='number',
                                   group_header='mtype',
                                   title='Number of Absolute Motions Greater than 0.2 mm')
        fig_rel_gt = ff.create_violin(rel_gt_df, data_header='number',
                                   group_header='mtype',
                                   title='Number of Relative Motions Greater than 0.1 mm')

        pyo.plot(fig_abs, filename=fname_abs, auto_open=False)
        pyo.plot(fig_rel, filename=fname_rel, auto_open=False)
        pyo.plot(fig_abs_gt, filename=fname_abs_gt, auto_open=False)
        pyo.plot(fig_rel_gt, filename=fname_rel_gt, auto_open=False)
        pass

    def connectome_analysis(thr=0.3, minimal=False, log=False,
                            hemispheres=False):
        """
        A function to threshold and binarize the connectomes.
        Presently just thresholds to reference correlation of
        setting all edges below 0.3 to 0, and those greater to 1.
        This value of 0.3 was generally the highest performing in
        discriminability analyses.

        **Positional Arguments:**
            - thr:
                - the threshold to binarize below.
        """
        self.graph_dir = "{}/graphs".format(self.outdir)
        cmd = "mkdir -p {}".format(self.graph_dir)
        mgu.execute_cmd(cmd)
        for label, raw_conn_files in self.connectomes.iteritems():
            label_raw = loadGraphs(raw_conn_files)
            label_graphs = []
            label_dir = "{}/{}".format(self.graph_dir, label)
            tmp_dir = "{}/graphs".format(tmp_dir)
            cmd = "mkdir -p {}".format(label_dir)
            mgu.execute_cmd(cmd)
            cmd = "mkdir -p {}".format(tmp_dir)
            mgu.execute_cmd(cmd)
            for subj, raw in label_raw:
                for u, v, d in raw.edges(data=True):
                    # threshold graphs
                    d['weight'] = (d['weight'] > thr).astype(int)
                gname = "{}/{}.gpickle".format(tmp_dir, subj)
                nx.write_gpickle(raw, gname)
                # so our graphs are in the format expected by
                # graphing qa
                label_graphs[subj] = gname
            compute_metrics(label_graphs, label_dir, label)
            outf = op.join(label_dir, "{}_plot".format(label)
            make_panel_plot(label_dir, outf, dataset=self.dataset,
                            atlas=label, minimal=minimal,
                            log=log, hemispheres=hemispheres)
        pass

