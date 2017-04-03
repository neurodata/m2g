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
import plotly.figure_factory as ff
from ndmg.stats.qa_func import qa_func as fqa
import numpy as np
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
        self.ndmgdir = basedir
        qadir = "{}/qa/".format(self.ndmgdir)
        self.outdir = outdir
        self.dataset = dataset

        (self.qa_files, self.subs) = self.get_qa_files()
        self.qa_objects = self.load_qa()
        self.group_level_analysis()
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
            sub_qa = "{}/{}_stats.pkl".format(sub)
            # if the files exists, add it to our qa_files
            if os.path.isfile(sub_qa)
                qa_files.append(sub_qa)
                subs.append(sub)
        return (qa_files, subs)

    def load_qa(self):
        """
        A function to load the quality control objects.
        """
        qa_objects = []
        for qa_file in qa_files:
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
        self_reg_sc = []
        temp_reg_sc = []
        for sub in self.qa_objects:
            self_reg_sc.append(sub.self_reg_sc)
            temp_reg_sc.append(sub.temp_reg_sc)
        fig_self = FF.create_violin(self_reg_sc,
                                    text=~paste('subject: ', self.subs)) 
        fig_temp = FF.create_violin(temp_reg_sc,
                                    text=~paste('subject: ', self.subs))

        fname_self = "self_reg_group.html"
        fname_temp = "temp_reg_group.html"
        # if a dataset name is provided, add it to the name
        if self.dataset is not None:
            fname_self = "{}_{}".format(self.dataset, fname_self)
            fname_temp = "{}_{}".format(self.dataset, fname_temp)
        pyo.plot(fig_self, filename=fname_self, auto_open=False)
        pyo.plot(fig_temp, filename=fname_temp, auto_open=False)
        pass

    def group_motion(self):
        """
        A function that performs group level motion corrective quality control.
        """
        dimension = ["x", "y", "z", "x", "y", "z"]
        motion = ["translation", "translation", "translation",
                  "rotation", "rotation", "rotation"]
        mean_per_dim = np.zeros(len(self.qa_objects), 6)

        for sub in self.qa_objects:
            abs_mc = sub.abs_pos
            rel_mc = sub.rel_pos
        pass
