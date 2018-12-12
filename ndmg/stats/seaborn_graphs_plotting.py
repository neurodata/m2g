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
# Created by Vivek Gopalakrishnan on 2018-12-11.
# Email: gkiar@jhu.edu

from argparse import ArgumentParser
import pickle
import numpy as np
import os
import matplotlib

matplotlib.use('Agg')  # very important above pyplot import
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn_helper as ss


def make_panel_plot(basepath, outf, dataset=None, atlas=None, minimal=True,
                    log=True, hemispheres=True, verb=False):
    fnames = [name for name in os.listdir(basepath)
              if os.path.splitext(name)[1] == '.pkl']
    fnames = sorted(fnames)
    paths = [os.path.join(basepath, item) for item in fnames]
    keys = ["_".join(n.split('.')[0].split('_')[1:]) for n in fnames]
    labs = [" ".join(n.split('.')[0].split('_')[1:]).title() for n in fnames]
    to_transform = ['locality_statistic_1', 'triangles']

    # Format subplots
    params = dict(context='talk', font_scale=1.3)
    c = float(4)
    r = np.ceil(len(keys) / c)
    with sns.plotting_context(**params):
        fig, axs = plt.subplots(
            nrows=int(r), ncols=int(c),
            dpi=500, figsize=(40., 30.)
        )

    for idx, (key, ax) in enumerate(zip(keys, axs.flatten())):

        if verb:
            print(labs[idx])

        f = open(paths[idx])
        dat = pickle.load(f)[keys[idx]]
        f.close()

        if key == 'number_non_zeros':
            ss.plot_rugdensity(
                dat.values(),
                ax,
                xlab='Number of Non-Zeros',
                ylab='Relative Probability',
                **params
            )
        elif key == 'edge_weight':
            edges = np.max([len(dat[i]) for i in dat.keys()])
            ss.plot_series(
                dat.values(),
                ax,
                xlab='Edge',
                ylab='Edge Weight',
                sort=True,
                log_transform=True,
                **params
            )
        elif key == 'degree_distribution':
            ss.plot_degrees(
                dat,
                ax,
                hemi=hemispheres,
                xlab='Node',
                ylab=labs[idx],
            )
        elif key == 'mean_connectome':
            if log:
                dat = np.log10(dat + 1)
            ss.plot_heatmap(
                dat,
                ax,
                title=labs[idx],
                **params
            )
        elif 'summary' in key:
            ss.plot_rugdensity(
                dat.values(),
                ax,
                title=labs[idx],
                xlab='Node',
                ylab='Count',
                **params
            )
        else:
            dims = len(dat.values()[0])
            ss.plot_series(
                dat.values(),
                ax,
                xlab='Node',
                ylab=labs[idx],
                title='',
                log_transform=True if key in to_transform else False,
                **params
            )

    # Master title
    if dataset is not None and atlas is not None:
        if atlas == 'desikan':
            atlas = atlas.capitalize()
        tit = dataset + ' Dataset (' + atlas + ' parcellation)'
    else:
        tit = None
    fig.suptitle(tit, fontsize=30)

    # Save
    fig.savefig(outf)


def main():
    parser = ArgumentParser(description="This is a graph qc plotting tool.")
    parser.add_argument("basepath", action="store", help="qc metric .pkl dir")
    parser.add_argument("dataset", action="store", help="dataset name")
    parser.add_argument("atlas", action="store", help="atlas name")
    parser.add_argument("outf", action="store", help="outfile name for plot")
    parser.add_argument("-v", "--verb", action="store_true", help="Verbose \
                        output statements.")
    r = parser.parse_args()

    make_panel_plot(r.basepath, r.outf, r.dataset, r.atlas, verb=r.verb)


if __name__ == "__main__":
    main()
