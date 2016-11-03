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
import matplotlib
matplotlib.use('Agg')  # very important above pyplot import

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


font = {'weight': 'bold',
        'size': 14}
matplotlib.rc('font', **font)

cols = '#000000'


class plot_metrics():

    def __init__(self, nnz, deg, ew, ccoefs, ss1, eigs, scree,
                 centrality, outf, suptit=None):
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
            scree:
                - dictionary of eigen values organizes for a scree plot
            centrality:
                - dictionary of betweenness centrality coefficients per graph
            outf:
                - string for outgoing figure file name
            suptit:
                - super title if you choose to have one
        """
        self.nnz = nnz
        self.deg = deg
        self.ew = ew
        self.ccoefs = ccoefs
        self.ss1 = ss1
        self.eigs = eigs
        self.scree = scree
        self.centrality = centrality
        self.color = cols
        self.outf = outf
        self.suptit = suptit
        self.plotting()

    def plotting(self):
        fig = plt.figure(figsize=(14, 6))

        i = 0
        # metric_list = [self.nnz, self.deg, self.ew, self.ccoefs, self.ss1,
        #                self.centrality, self.eigs, self.scree]
        # name_list = ['NNZ', 'log(Degree)', 'log(Edge Weight)',
        #              'log(Clustering Coefficient)', 'log(Max Locality Stat)',
        #              'log(Centrality)', 'Spectrum', 'Scree Plot']
        # type_list = ['sc', 'hi', 'hi', 'hi', 'hi', 'hi', 'se', 'se']
        metric_list = [self.nnz, self.deg, self.ew, self.ccoefs, self.ss1,
                       self.centrality, self.eigs]
        name_list = ['NNZ', 'Degree', 'Edge Weight',
                     'Clustering Coefficient', 'Scan Statistic-1',
                     'Centrality', 'Spectrum']
        type_list = ['sc', 'hi', 'hi', 'hi', 'hi', 'hi', 'se']
        for idx, val in enumerate(metric_list):
            i += 1
            ax = plt.subplot(2, 4, i)
            plt.hold(True)
            self.plot_helper(ax, val, name_list[idx], typ=type_list[idx])

        fig.tight_layout()
        if self.suptit is not None:
            t = plt.suptitle(self.suptit, y=1.04, size=20)
            plt.savefig(self.outf, bbox_inches='tight', bbox_extra_artists=[t])
        else:
            plt.savefig(self.outf, bbox_inches='tight')

        metadata = {"subjects": self.nnz.keys(),
                    "date": time.asctime(time.localtime())}
        with open(os.path.splitext(self.outf)[0]+'_info.json', 'w') as fp:
            json.dump(metadata, fp)

    def set_tick_labels(self, ax, miny, maxy):
        po = np.floor(np.log10(maxy))
        miny = 0 if miny < 10**(po-1) else self.round_to_n(miny/(10**po), 2)
        maxy = self.round_to_n(maxy/(10**po), 2)

        labels = [miny,
                  (maxy+miny)/2,
                  maxy]
        ax.set_yticklabels(labels)
        ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f'))
        if po == 0:
            return ''
        else:
            return ' (x 10^%d)' % po

    def round_to_n(self, x, n):
        return round(x, (n-1)-int(np.floor(np.log10(abs(x)))))

    def plot_helper(self, ax, data, tit, typ='hi'):
        maxy = float('-inf')
        miny = float('inf')
        if typ == 'hi':
            alpha = np.min((1, 2.0/len(data['pdfs'])))
            for subj in data['pdfs']:
                x = data['xs'][subj]
                y = data['pdfs'][subj]
                ty = np.max(y)
                maxy = ty if ty > maxy else maxy
                ty = np.min(y)
                miny = ty if ty < miny else miny
                #plt.plot(np.log(x+1), y, color=self.color, alpha=alpha)
                plt.plot(x, y, color=self.color, alpha=alpha)
            modif = self.set_tick_labels(ax, miny, maxy)
            plt.ylabel('Density'+modif)
        elif typ == 'se':
            alpha = np.min((1, 2.0/len(data)))
            for subj in data:
                x = np.linspace(1, len(data[subj]), len(data[subj]))
                y = data[subj]
                ty = np.max(y)
                maxy = ty if ty > maxy else maxy
                ty = np.min(y)
                miny = ty if ty < miny else miny
                plt.plot(x, y, color=self.color, alpha=alpha)
            modif = self.set_tick_labels(ax, miny, maxy)
            if tit is 'Spectrum':
                plt.ylabel('Eigenvalue'+modif)
            else:
                plt.ylabel('Portion of Total Variance')
        elif typ == 'sc':
            x = 0
            y = data.values()
            if len(y) <= 1:
                plt.scatter(0, y, color=self.color)
                plt.xlim([-0.5, 0.5])
            else:
                voil = plt.violinplot(y)
                voil['bodies'][0].set_color(self.color)
            plt.ylabel('Count')

        if typ == 'sc':
            plt.ylim([np.min(y)*0.9, np.max(y)*1.1])
            plt.xticks([])
            plt.yticks([np.min(y), np.max(y)])
        else:
            if typ == 'se':
                plt.xlim([np.min(x), np.max(x)])
                plt.xticks([np.min(x),  np.max(x)])
            else:
                plt.xlim([np.min(x), np.max(x)])
                plt.xticks([np.min(x),  np.max(x)])
                # plt.xlim([np.min(np.log(x+1)), np.max(np.log(x+1))])
                # plt.xticks([np.min(np.log(x+1)),  np.max(np.log(x+1))])
            plt.ylim([miny, maxy])
            plt.yticks([miny, ((maxy - miny)/2), maxy])

        plt.title(tit, y=1.04)

    def rand_jitter(self, arr):
        stdev = .03*(max(arr)-min(arr)+2)
        return arr + np.random.randn(len(arr)) * stdev

    def factors(self, N):
        factors = [subitem for subitem in [(i, N//i)
                   for i in range(1, int(N**0.5) + 1)
                   if N % i == 0 and i > 1]]
        return set([fact for item in factors for fact in item])
