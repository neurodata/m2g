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
from plotly.tools import FigureFactory as ff
from ndmg.stats.qa_func import qa_func as fqa
import numpy as np
import ndmg.utils as mgu
import os


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
        print np.__version__
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
            print sub
            sub_qa = "{}/{}/{}_stats.pkl".format(self.qadir, sub, sub)
            # if the files exists, add it to our qa_files
            print sub_qa
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
        for dataset in os.listdir(self.conn_dir):
            this_dataset = []
            dataset_dir = "{}/{}/".format(self.conn_dir, dataset)
            for connectome in os.listdir(dataset_dir):
                if os.path.isfile(connectome):
                    this_dataset.append(connectome)
            connectomes[dataset] = this_dataset
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
        fig_self = ff.create_violin(self_reg_sc)
                                    #yaxis=dict(title="Registration Score"),
                                    #name="Subject Self Registration",
                                    #text='subject: {}'.format(self.subs))
        fig_temp = ff.create_violin(temp_reg_sc)
                                    #yaxis=dict(title="Registration Score"),
                                    #name="Subject Template Registration",
        fig_cnr = ff.create_violin(cnr)
                                   #yaxis=dict(title="Contrast-to-Noise Ratio"),
                                   #name="Contrast to Noise after Registration",
        fig_snr = ff.create_violin(snr)
                                   #name="Contrast to Noise after Registration",
                                   #yaxis=dict(title="Contrast-to-Noise Ratio"),

        fname_self = "self_reg_group.html"
        fname_temp = "temp_reg_group.html"
        fname_cnr = "cnr_reg_group.html"
        fname_snr = "snr_reg_group.html"
        # if a dataset name is provided, add it to the name
        if self.dataset is not None:
            fname_self = "{}_{}".format(self.dataset,
                                           fname_self)
            fname_temp = "{}_{}".format(self.dataset,
                                           fname_temp)
            fname_cnr = "{}_{}".format(self.dataset,
                                          fname_cnr)
            fname_snr = "{}_{}".format(self.dataset,
                                          fname_snr)
        fname_self = "{}/{}".format(regdir, fname_self)
        fname_temp = "{}/{}".format(regdir, fname_temp)
        fname_cnr = "{}/{}".format(regdir, fname_cnr)
        fname_snr = "{}/{}".format(regdir, fname_snr)
        pyo.plot(fig_snr, filename=fname_snr, auto_open=False)
        pyo.plot(fig_self, filename=fname_self, auto_open=False)
        pyo.plot(fig_temp, filename=fname_temp, auto_open=False)
        pyo.plot(fig_cnr, filename=fname_cnr, auto_open=False)
        pass

    def group_motion(self):
        """
        A function that performs group level motion corrective quality control.
        """
        mcdir = "{}/{}".format(self.outdir, "mc")
        cmd = "mkdir -p {}".format(mcdir)
        mgu.execute_cmd(cmd)

        dimension = ["x", "y", "z", "x", "y", "z"]
        motion = ["translation", "translation", "translation",
                  "rotation", "rotation", "rotation"]

        mean_per_dim = np.zeros((len(self.qa_objects), 6))

        for sub in self.qa_objects:
            abs_mc = sub.abs_pos
            rel_mc = sub.rel_pos

        trans_abs = np.linalg.norm(abs_mc[:, 3:6], axis=1)
        trans_rel = np.linalg.norm(abs_mc[:, 3:6], axis=1)
        fname_abs = "trans_absolute_group.html"
        fname_rel = "trans_relative_group.html"
        # if a dataset name is provided, add it to the name
        if self.dataset is not None:
            fname_abs = "{}/{}_{}".format(mcdir, self.dataset,
                                          fname_self)
            fname_rel = "{}/{}_{}".format(mcdir, self.dataset,
                                          fname_temp)
 
        fig_abs = ff.create_violin(trans_abs)
                                    #name="Mean Absolute Translation from Volume to Volume",
                                    #text='subject: {}'.format(self.subs))
                                    #yaxis=dict(title="Registration Score"),
        fig_rel = ff.create_violin(trans_rel)
                                    #name="Mean Relative Translation from Volume to Volume",
                                    #text='subject: {}'.format(self.subs))
                                    #yaxis=dict(title="Registration Score"),
        pyo.plot(fig_abs, filename=fname_abs, auto_open=False)
        pyo.plot(fig_rel, filename=fname_rel, auto_open=False)
        pass

    def connectome_analysis(self):
        """
        A function that calls ndmg group analysis script for each connectome,
        at each scale.
        """
        pass
