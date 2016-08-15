#!/usr/bin/env python

# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

# graph_qc.py
# Created by Greg Kiar on 2016-05-11.
# Email: gkiar@jhu.edu

import time
import json
import sys
import os
import numpy as np
import networkx as nx
import matplotlib; matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

font = {'weight': 'bold',
        'size': 14}
matplotlib.rc('font', **font)

cols = '#000000'


class plot_metrics():

    def __init__(self, nnz, deg, ew, ccoefs, ss1, eigs, centrality, outf):
        """
        Visualizes the computed summary statistics for each atlas

        Required Parameters:
            nnz:
                - dictionary of number of non-zero edges per graph
            deg:
                - dictionary of degree distributions per graph
            ew:
                - dictionary of edge weight distributions per graph
            ccoefs:
                - dictionary of clustering coefficients per graph
            ss1:
                - dictionary of scan statistic-1 distributions per graph
            eigs:
                - dictionary of eigen sequence per graph
            centrality:
                - dictionary of betweenness centrality coefficients per graph
            outf:
                - string for outgoing figure file name
        """
        self.nnz = nnz
        self.deg = deg
        self.ew = ew
        self.ccoefs = ccoefs
        self.ss1 = ss1
        self.eigs = eigs
        self.centrality = centrality
        self.color = cols
        self.outf = outf
        self.plotting()

    def plotting(self):
        fig = plt.figure(figsize=(14, 6))

        i = 0
        metric_list = [self.nnz, self.deg, self.ew, self.ccoefs, self.ss1,
                       self.centrality, self.eigs]
        name_list = ['NNZ', 'Degree', 'Edge Weight', 'Clustering Coefficient',
                     'Scan Statistic-1', 'Centrality', 'Eigen']
        type_list = ['sc', 'hi', 'hi', 'hi', 'hi', 'hi', 'se']
        for idx, val in enumerate(metric_list):
            i += 1
            ax = plt.subplot(2, 4, i)
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%2.1e'))
            plt.hold(True)
            self.plot_helper(val, name_list[idx], typ=type_list[idx])

        fig.tight_layout()

        plt.savefig(self.outf, bbox_inches='tight')
        # plt.show()

        metadata = {"subjects": self.nnz.keys(),
                    "date": time.asctime(time.localtime())}
        with open(os.path.splitext(self.outf)[0]+'_info.json', 'w') as fp:
            json.dump(metadata, fp)

    def plot_helper(self, data, tit, typ='hi'):
        maxy = float('-inf')
        if typ == 'hi':
            for subj in data['pdfs']:
                x = data['xs'][subj]
                y = data['pdfs'][subj]
                ty = np.max(y)
                maxy = ty if ty > maxy else maxy
                plt.plot(x, y, color=self.color, alpha=0.1)
        elif typ == 'se':
            for subj in data:
                x = np.linspace(1, len(data[subj]), len(data[subj]))
                y = data[subj]
                ty = np.max(y)
                maxy = ty if ty > maxy else maxy
                plt.plot(x, y, color=self.color, alpha=0.1)
        elif typ == 'sc':
            x = self.rand_jitter([0]*len(data.values()))
            y = data.values()
            plt.scatter(x, y, alpha=0.1, color=self.color)

        if typ == 'sc':
            plt.xlim([np.mean(x)-0.2, np.mean(x)+0.2])
            plt.ylim([0, np.max(data.values())*1.1])
            plt.xticks([])
            plt.yticks([0, (np.max(y))/2, np.max(y)])
        else:
            plt.xlim([np.min(x), np.max(x)])
            plt.ylim([np.min(y), maxy])
            plt.xticks([np.min(x),  np.max(x)])
            plt.yticks([np.min(y), (np.max(y) - np.min(y))/2, np.max(y)])

        plt.title(tit, y=1.04)

    def rand_jitter(self, arr):
        stdev = .03*(max(arr)-min(arr)+2)
        return arr + np.random.randn(len(arr)) * stdev

    def factors(self, N):
        factors = [subitem for subitem in [(i, N//i)
                   for i in range(1, int(N**0.5) + 1)
                   if N % i == 0 and i > 1]]
        return set([fact for item in factors for fact in item])
