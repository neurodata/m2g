#!/usr/bin/env python

from argparse import ArgumentParser
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot, plot
import pickle
import plotly_panels as pp
import os

# init_notebook_mode()

def make_panel_plot(basepath, outf, dataset=None, atlas=None):
    # basepath = '/Users/gkiar/code/ocp/scratch/aug15/qc/desikan/'
    # dataset = 'NKI1'
    # atlas = 'Desikan'
    
    fnames = [name for name in os.listdir(basepath)
              if os.path.splitext(name)[1] == '.pkl']
    fnames = sorted(fnames)
    paths = [os.path.join(basepath, item) for item in fnames]
    keys = ["_".join(n.split('.')[0].split('_')[1:]) for n in fnames]
    rela = 'Count'
    ylabs = [rela, rela, rela, rela,
             'Eigenvalue', rela, rela, 'Portion of Total Variance']
    xlabs = ['Betweenness Centrality', 'Clustering Coefficient', 'Degree',
             'Edge Weight', 'Dimension', 'Number of Non-zeros',
             'Locality Statistic-1', 'Dimension']
    
    traces = list(())
    for idx, curr in enumerate(paths):
        f = open(curr)
        dat = pickle.load(f)[keys[idx]]
        f.close()
        if keys[idx] == 'number_non_zeros':
            fig = pp.plot_rugdensity(dat.values())
        elif keys[idx] == 'eigen_sequence' or keys[idx] == 'scree_eigen':
            dims = len(dat.values()[0])
            fig = pp.plot_series(dat.values())
        else:
            xs = dat['xs'].values()
            ys = dat['pdfs'].values()
            fig = pp.plot_density(xs, ys)
        traces += [pp.fig_to_trace(fig)]
    
    multi = pp.traces_to_panels(traces)
    for idx, curr, in enumerate(paths):
        key = 'axis%d' % (idx+1)
        d = multi.layout['x'+key]['domain']
        multi.layout['x'+key]['domain'] = [d[0], d[1]-0.0125]
        multi.layout['y'+key]['zeroline'] = False
        multi.layout['x'+key]['zeroline'] = False
        multi.layout['x'+key]['title'] = xlabs[idx]
        multi.layout['y'+key]['title'] = ylabs[idx]
        multi.layout['x'+key]['nticks'] = 3
        multi.layout['y'+key]['nticks'] = 3
        if idx in [0, 3, 6]:
            multi.layout['x'+key]['type'] = 'log'
            multi.layout['x'+key]['title'] += ' (log scale)'
        if idx in [4, 7]:
            multi.layout['x'+key]['range'] = [1, dims]
            multi.layout['x'+key]['tickvals'] = [1, dims/2, dims]
            if idx in [7]:
                multi.layout['y'+key]['range'] = [0, 1]
                multi.layout['y'+key]['tickvals'] = [0, 0.5, 1]
        if idx in [1]:
            multi.layout['x'+key]['range'] = [0, 1] 
    
    if dataset is not None and atlas is not None:
        if atlas == 'desikan':
            atlas = atlas.capitalize() 
        tit = dataset + ' Dataset (' + atlas + ' parcellation)'
    else:
        tit = None
    multi.layout['title'] = tit
    # iplot(multi, validate=False)
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
