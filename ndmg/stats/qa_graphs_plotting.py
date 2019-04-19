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
#

# qa_graphs_plotting.py
# Created by Greg Kiar on 2016-09-19.
# Email: gkiar@jhu.edu

import warnings

warnings.simplefilter("ignore")
from argparse import ArgumentParser
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import pickle
from . import plotly_helper as pp
import numpy as np
import os


def make_panel_plot(
    basepath,
    outf,
    dataset=None,
    atlas=None,
    minimal=True,
    log=True,
    hemispheres=True,
    modality="dwi",
):
    fnames = [
        name for name in os.listdir(basepath) if os.path.splitext(name)[1] == ".pkl"
    ]
    fnames = sorted(fnames)
    paths = [os.path.join(basepath, item) for item in fnames]
    keys = ["_".join(n.split(".")[0].split("_")[2:]) for n in fnames]
    print(fnames)
    print(keys)
    if modality == "dwi":
        modtit = "DWI"
        order = [0, 1, 2, 5, 4, 3, 6, 7]
        keys = [keys[o] for o in order]
        paths = [paths[o] for o in order]
        labs = [
            "Betweenness Centrality",
            "Clustering Coefficient",
            "Degree",
            "Locality Statistic-1",
            "Eigenvalue",
            "Edge Weight",
            "Number of Non-zeros",
            "Mean Connectome",
        ]
    else:
        modtit = "fMRI"
        order = [0, 1, 2, 6, 4, 3, 5, 7]
        keys = [keys[o] for o in order]
        paths = [paths[o] for o in order]

        labs = [
            "Betweenness Centrality",
            "Clustering Coefficient",
            "Degree",
            "Average Path Length",
            "Locality Statistic-1",
            "Eigenvalue",
            "Number of Non-zeros",
            "Mean Connectome",
        ]
    traces = list(())
    for idx, curr in enumerate(paths):
        f = open(curr)
        dat = pickle.load(f)[keys[idx]]
        f.close()
        if keys[idx] == "number_non_zeros":
            fig = pp.plot_rugdensity(list(dat.values()))
        elif keys[idx] == "edge_weight":
            edges = np.max([len(dat[i]) for i in list(dat.keys())])
            fig = pp.plot_series(list(dat.values()), sort=True)
        elif keys[idx] == "degree_distribution":
            fig = pp.plot_degrees(dat, hemi=hemispheres)
            if hemispheres:
                maxdat = np.max(
                    [np.max(dat[key][k]) for key in list(dat.keys()) for k in dat[key]]
                )
                anno = [
                    dict(
                        x=dims / 3,
                        y=4 * float(maxdat / 7),
                        xref="x3",
                        yref="y3",
                        text="ipsilateral",
                        showarrow=False,
                        font=dict(color="rgba(0.0,0.0,0.0,0.6)", size=14),
                    ),
                    dict(
                        x=dims / 3,
                        y=3.7 * float(maxdat / 7),
                        xref="x3",
                        yref="y3",
                        text="contralateral",
                        showarrow=False,
                        font=dict(color="rgba(0.11,0.62,0.47,0.6)", size=14),
                    ),
                ]
        elif keys[idx] == "study_mean_connectome":
            if log:
                dat = np.log10(dat + 1)
            fig = pp.plot_heatmap(dat, name=labs[idx])
        else:
            dims = len(list(dat.values())[0])
            fig = pp.plot_series(list(dat.values()))
        traces += [pp.fig_to_trace(fig)]

    multi = pp.traces_to_panels(traces)
    for idx, curr in enumerate(paths):
        key = "axis%d" % (idx + 1)
        d = multi.layout["x" + key]["domain"]
        multi.layout["x" + key]["domain"] = [d[0], d[1] - 0.0125]
        multi.layout["x" + key]["zeroline"] = False
        multi.layout["y" + key]["zeroline"] = False
        multi.layout["y" + key]["title"] = ""
        multi.layout["x" + key]["title"] = "Node"
        multi.layout["x" + key]["nticks"] = 3
        multi.layout["y" + key]["nticks"] = 3
        if (idx in [0, 1, 2, 3, 4, 5] and modality == "func") or (
            idx in [0, 1, 2, 3, 4, 5] and modality == "dwi"
        ):
            multi.layout["x" + key]["range"] = [1, dims]
            multi.layout["x" + key]["tickvals"] = [1, dims / 2, dims]
            if idx in [2]:
                if hemispheres:
                    multi.layout["annotations"] = anno
            elif log:
                multi.layout["y" + key]["type"] = "log"
                multi.layout["y" + key]["title"] += "log"
        if idx in [5] and modality == "dwi":
            multi.layout["x" + key]["range"] = [1, edges]
            multi.layout["x" + key]["tickvals"] = [1, edges / 2, edges]
            multi.layout["x" + key]["title"] = "Edge"
        if (idx in [4] and modality == "dwi") or (idx in [5] and modality == "func"):
            multi.layout["x" + key]["range"] = [1, dims]
            multi.layout["x" + key]["tickvals"] = [1, dims / 2, dims]
            multi.layout["x" + key]["title"] = "Dimension"
        multi.layout["y" + key]["title"] += labs[idx]
        if idx in [6]:
            multi.layout["y" + key]["title"] = "Relative Probability"
            multi.layout["x" + key]["title"] = labs[idx]
        if idx in [7]:
            multi.layout["y" + key]["title"] = None
            multi.layout["x" + key]["title"] = labs[idx]
            multi.layout["y" + key]["autorange"] = "reversed"
            multi.layout["x" + key]["tickvals"] = [0, dims / 2 - 1, dims - 1]
            multi.layout["y" + key]["tickvals"] = [0, dims / 2 - 1, dims - 1]
            multi.layout["x" + key]["ticktext"] = [1, dims / 2, dims]
            multi.layout["y" + key]["ticktext"] = [1, dims / 2, dims]
            if log:
                multi.layout["x" + key]["title"] += " (log10)"
    if dataset is not None and atlas is not None:
        if atlas == "desikan":
            atlas = atlas.capitalize()
        tit = "{} Dataset ({} parcellation), {} Group Analysis".format(
            dataset, atlas, modtit
        )
    else:
        tit = "{} Group Analysis".format(modtit)
    multi.layout["title"] = tit
    # iplot(multi, validate=False)

    if minimal:
        locs = [idx for idx, d in enumerate(multi.data) if d["yaxis"] == "y8"]
        for l in locs:
            multi.data[l] = {}
        multi.layout["x" + key]["title"] = ""
        multi.layout["y" + key]["title"] = ""
        multi = pp.panel_invisible(multi, 8)

    plot(multi, validate=False, filename=outf + ".html")


def main():
    parser = ArgumentParser(description="This is a graph qc plotting tool.")
    parser.add_argument("basepath", action="store", help="qc metric .pkl dir")
    parser.add_argument("dataset", action="store", help="dataset name")
    parser.add_argument("atlas", action="store", help="atlas name")
    parser.add_argument("outf", action="store", help="outfile name for plot")
    r = parser.parse_args()

    make_panel_plot(r.basepath, r.outf, r.dataset, r.atlas)


if __name__ == "__main__":
    main()
