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

from argparse import ArgumentParser
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot, plot
import pickle
import plotly_helper as pp
import numpy as np
import os


def make_panel_plot(basepath, outf, dataset=None, atlas=None, minimal=True,
                    log=True, hemispheres=True):
    fnames = [name for name in os.listdir(basepath)
              if os.path.splitext(name)[1] == '.pkl']
    fnames = sorted(fnames)
    store = {}
    for item in fnames:
        store[item] = {'path': os.path.join(basepath, item),
                       'key': "_".join(item.split('.')[0].split('_')[1:]),
                       'label': " ".join(item.split('.')[0].split('_')[1:]).title()
                       }

    traces = list(())
    # import pdb; pdb.set_trace()
    for idx, curr in enumerate(store.values()):
        f = open(curr['path'])
        dat = pickle.load(f)[curr['key']]
        f.close()
        if curr['key'] == 'number_non_zeros':
            fig = pp.plot_rugdensity(dat.values())
        elif curr['key'] == 'edge_weight':
            edges = np.max([len(dat[i]) for i in dat.keys()])
            fig = pp.plot_series(dat.values(), sort=True)
        elif curr['key'] == 'degree_distribution':
            fig = pp.plot_degrees(dat, hemi=hemispheres)
            if hemispheres:
                dims = len(dat.values()[0])
                anno = [dict(x=dims/3,
                             y=4*dims/7,
                             xref='x3',
                             yref='y3',
                             text='ipsilateral',
                             showarrow=False,
                             font=dict(color='rgba(0.0,0.0,0.0,0.6)',
                                       size=14)),
                        dict(x=dims/3,
                             y=3.7*dims/7,
                             xref='x3',
                             yref='y3',
                             text='contralateral',
                             showarrow=False,
                             font=dict(color='rgba(0.11,0.62,0.47,0.6)',
                                       size=14))]
        elif curr['key'] == 'study_mean_connectome':
            if log:
                dat = np.log10(dat+1)
            fig = pp.plot_heatmap(dat, name=curr['label'])
        else:
            dims = len(dat.values()[0])
            # layout = pp.std_layout(ylab=curr['label'], xlab='Graph')
            fig = pp.plot_series(dat.values())
            fig['layout']['xaxis']['title'] = 'Node'
            fig['layout']['yaxis']['title'] = curr['label']
            # fig.layout = layout
        traces += [pp.fig_to_trace(fig)]

    multi = pp.traces_to_panels(traces)
    for idx, curr, in enumerate(store.values()):
        key = 'axis%d' % (idx+1)
        d = multi.layout['x'+key]['domain']
        multi.layout['x'+key]['domain'] = [d[0], d[1]-0.0125]
        multi.layout['x'+key]['zeroline'] = False
        multi.layout['y'+key]['zeroline'] = False
        multi.layout['y'+key]['title'] = curr['label']
        multi.layout['x'+key]['title'] = 'Node'
        multi.layout['x'+key]['nticks'] = 3
        multi.layout['y'+key]['nticks'] = 3
        # Edge weight
        if curr['key'] in ['edge_weight']:
            multi.layout['x'+key]['range'] = [1, edges]
            multi.layout['x'+key]['tickvals'] = [1, edges/2, edges]
            multi.layout['x'+key]['title'] = 'Edge'
        # Eigenvalue
        elif curr['key'] in ['eigen_sequence']:
            multi.layout['x'+key]['range'] = [1, dims]
            multi.layout['x'+key]['tickvals'] = [1, dims/2, dims]
            multi.layout['x'+key]['title'] = 'Dimension'
        # Number of Non-zeros
        elif curr['key'] in ['number_non_zeros']:
            multi.layout['x'+key]['title'] = curr['label']
        # Mean Connectome
        elif curr['key'] in ['study_mean_connectome']:
            multi.layout['y'+key]['title'] = None
            multi.layout['x'+key]['title'] = curr['label']
            multi.layout['y'+key]['autorange'] = 'reversed'
            multi.layout['x'+key]['tickvals'] = [0, dims/2-1, dims-1]
            multi.layout['y'+key]['tickvals'] = [0, dims/2-1, dims-1]
            multi.layout['x'+key]['ticktext'] = [1, dims/2, dims]
            multi.layout['y'+key]['ticktext'] = [1, dims/2, dims]
            if log:
                multi.layout['x'+key]['title'] += ' (log10)'
        else:
            multi.layout['x'+key]['range'] = [1, dims]
            multi.layout['x'+key]['tickvals'] = [1, dims/2, dims]
            # Degree
            if curr['key'] in ['degree_distribution']:
                if hemispheres:
                    multi.layout['annotations'] = anno
            elif log:
                multi.layout['y'+key]['type'] = 'log'
                multi.layout['y'+key]['title'] += ' (log scale)'        

    if dataset is not None and atlas is not None:
        if atlas == 'desikan':
            atlas = atlas.capitalize()
        tit = dataset + ' Dataset (' + atlas + ' parcellation)'
    else:
        tit = None
    multi.layout['title'] = tit
    # iplot(multi, validate=False)

    if minimal:
        locs = [idx for idx, d in enumerate(multi.data) if d['yaxis'] == 'y8']
        for l in locs:
            multi.data[l] = {}
        multi.layout['x'+key]['title'] = ''
        multi.layout['y'+key]['title'] = ''
        multi = pp.panel_invisible(multi, 8)

    plot(multi, validate=False, filename=outf+'.html')


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
