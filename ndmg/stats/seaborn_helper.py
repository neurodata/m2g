#!/usr/bin/env python

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

# seaborn_helper.py
# Created by Vivek Gopalakrishnan on 2018-12-10.
# Email: gkiar@jhu.edu

import numpy as np
import matplotlib

matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt
import seaborn as sns


# Plotting functions
def plot_heatmap(dats, ax, title='', ylab='', xlab='',
                 context=None, font_scale=None):
    with sns.plotting_context(context=context, font_scale=font_scale):
        plot = sns.heatmap(
            dats,
            cmap='viridis',
            cbar=False,
            square=True,
            xticklabels=False,
            yticklabels=False,
            ax=ax,
        )
    std_layout(ax, title, ylab, xlab, format_range=False)


def plot_degrees(dats, ax, title='', ylab='', xlab='', hemi=True,
                 context=None, font_scale=None):
    if hemi:
        main = dats['ipso_deg']
        contra = dats['contra_deg']
    else:
        main = dats['total_deg']
    al = (4.0 / len(main.keys()))

    with sns.plotting_context(context=context, font_scale=font_scale):
        for idx, key in enumerate(main.keys()):
            lgth = len(main[key])
            plot = sns.lineplot(
                x=np.linspace(1, lgth, lgth),
                y=main[key],
                color='#000000',
                alpha=float('%1.2f' % al),
                ax=ax,
            )
            plot = sns.lineplot(
                x=np.linspace(1, lgth, lgth),
                y=contra[key],
                color='#0B622F',
                alpha=float('%1.2f' % al),
                ax=ax,
            )

        # Legend
        ax.text(40, 31, 'ipsilateral', color='#000000')
        ax.text(40, 33, 'contralateral', color='#0B622F')
    std_layout(ax, title, ylab, xlab)


def plot_series(dats, ax, title='', ylab='', xlab='', sort=False,
                context=None, font_scale=None, log_transform=False):
    with sns.plotting_context(context=context, font_scale=font_scale):
        for idx, ys in enumerate(dats):
            if sort:
                ys = np.sort(ys)
            sns.lineplot(
                x=np.linspace(1, len(ys), len(ys)),
                y=ys,
                color='#000000',
                alpha=float('%1.2f' % (4.0 / len(dats))),
                ax=ax,
            )
        if log_transform:
            ax.set_yscale('log')
            ylab = ylab + ' (log scale)'
    std_layout(ax, title, ylab, xlab)


def plot_rugdensity(series, ax, title='', ylab='', xlab='',
                    context=None, font_scale=None):
    with sns.plotting_context(context=context, font_scale=font_scale):
        sns.distplot(
            series,
            rug=True,
            hist=False,
            norm_hist=False,
            color='#000000',
            ax=ax
        )
    std_layout(ax, title, ylab, xlab)


# Helper functions
def std_layout(ax, title, ylab, xlab, format_range=True):
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    if format_range:
        range = ax.get_xticks()
        ax.set_xticks([min(range), np.median(range), max(range)])
        ax.yaxis.set_major_locator(plt.MaxNLocator(3))
