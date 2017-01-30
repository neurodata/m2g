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

# plotly_helper.py
# Created by Greg Kiar on 2016-09-19.
# Email: gkiar@jhu.edu

import numpy as np
from scipy.stats import gaussian_kde
from itertools import product
from plotly.graph_objs import *
from plotly import tools


def plot_heatmap(dats, name=None, ylab=None, xlab=None):
    data = [
            Heatmap(
                    z=dats,
                    name=name,
                    showscale=False,
                    colorscale='Viridis'
                   )
           ]
    layout = std_layout(name, ylab, xlab)
    fig = Figure(data=data, layout=layout)
    return fig


def plot_degrees(dats, name=None, ylab=None, xlab=None, hemi=True):
    data = list()
    if hemi:
        main = dats['ipso_deg']
        contra = dats['contra_deg']
    else:
        main = dats['total_deg']
    al = (4.0/len(main.keys()))

    for key in main.keys():
        lgth = len(main[key])
        data += [
                 Scatter(
                         x=np.linspace(1, lgth, lgth),
                         y=main[key],
                         line=Line(
                                   color='rgba(0,0,0,%1.2f)' % al
                                  ),
                         hoverinfo='x',
                         name=name,
                        )
                ]
        if hemi:
            data += [
                     Scatter(
                             x=np.linspace(1, lgth, lgth),
                             y=contra[key],
                             line=Line(
                                       color='rgba(0.11,0.62,0.47,%1.2f)' % al
                                      ),
                             hoverinfo='x',
                             name=name,
                            )
                    ]
    layout = std_layout(name, ylab, xlab)
    fig = Figure(data=data, layout=layout)
    return fig


def plot_series(dats, name=None, ylab=None, xlab=None, sort=False):
    data = list()
    for idx, ys in enumerate(dats):
        if sort:
            ys = np.sort(ys)
        data += [
                 Scatter(
                         x=np.linspace(1, len(ys), len(ys)),
                         y=ys,
                         line=Line(
                                   color='rgba(0,0,0,%1.2f)' % (4.0/len(dats))
                                  ),
                         hoverinfo='x',
                         name=name,
                        )
                ]
    layout = std_layout(name, ylab, xlab)
    fig = Figure(data=data, layout=layout)
    return fig


def plot_density(xs, ys, name=None, ylab=None, xlab=None):
    data = list()
    for idx, x in enumerate(xs):
        data += [
                 Scatter(
                         x=xs[idx],
                         y=ys[idx],
                         line=Line(
                                   color='rgba(0,0,0,%1.2f)' % (4.0/len(ys))
                                  ),
                         hoverinfo='x',
                         name=name,
                        )
                ]
    layout = std_layout(name, ylab, xlab)
    fig = Figure(data=data, layout=layout)
    return fig


def plot_rugdensity(series, name=None, ylab=None, xlab=None):
    if len(series) > 1:
        dens = gaussian_kde(series)
        x = np.linspace(np.min(series), np.max(series), 100)
        y = dens.evaluate(x)*np.max(series)

        d_rug = Scatter(
                    x=series,
                    y=[0]*len(series),
                    mode='markers',
                    marker=Marker(
                             color='rgba(0,0,0,0.9)',
                             symbol='line-ns-open',
                             size=10,
                             opacity=0.5
                           ),
                    name=name
              )
    else:
        x = 0
        y = series

    d_dens = Scatter(
                x=x,
                y=y,
                line=Line(
                       color='rgba(0,0,0,0.9)'
                     ),
                hoverinfo='x',
                name=name,
           )
    if len(series) > 1:
        data = [d_dens, d_rug]
    else:
        data = [d_dens]
    layout = std_layout(name, ylab, xlab)
    fig = Figure(data=data, layout=layout)
    return fig


def std_layout(name=None, ylab=None, xlab=None):
    return Layout(
            title=name,
            showlegend=False,
            xaxis={'nticks': 5,
                   'title': xlab},
            yaxis={'nticks': 3,
                   'title': ylab}
          )


def fig_to_trace(fig):
    data = fig['data']
    for item in data:
        item.pop('xaxis', None)
        item.pop('yaxis', None)
    return data


def traces_to_panels(traces, names=[], ylabs=None, xlabs=None):
    r, c, locs = panel_arrangement(len(traces))
    multi = tools.make_subplots(rows=r, cols=c, subplot_titles=names)
    for idx, loc in enumerate(locs):
        if idx < len(traces):
            for component in traces[idx]:
                multi.append_trace(component, *loc)
        else:
            multi = panel_invisible(multi, idx+1)
    multi.layout['showlegend'] = False
    return multi


def panel_arrangement(num):
    dims = list()
    count = 0
    while len(dims) == 0:
        dims = list(factors(num+count))
        count += 1

    if len(dims) == 1:
        row = col = dims[0]
    else:
        row = dims[0]
        col = dims[-1]

    locations = [(a+1, b+1) for a, b in product(range(row), range(col))]
    return row, col, locations


def panel_invisible(plot, idx):
    for c in ['x', 'y']:
        axe = c+'axis'+str(idx)
        plot.layout[axe]['showgrid'] = False
        plot.layout[axe]['zeroline'] = False
        plot.layout[axe]['showline'] = False
        plot.layout[axe]['showticklabels'] = False
    return plot


def rand_jitter(arr):
    stdev = .03*(max(arr)-min(arr)+2)
    return arr + np.random.randn(len(arr)) * stdev


def factors(N):
    return set([item for subitem in
                [(i, N//i) for i in range(1, int(N**0.5) + 1)
                 if N % i == 0 and i > 1]
               for item in subitem])
