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

# qc.py
# Created by Eric W Bridgeford on 2016-06-08.
# Email: ebridge2@jhu.edu

from numpy import ndarray as nar
from scipy.stats import gaussian_kde
from ndmg.utils import gen_utils as mgu
import numpy as np
import nibabel as nb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ndmg.stats.qa_reg import plot_overlays
import plotly as py
import plotly.offline as offline
from plotly.graph_objs import Heatmap
import plotly_helper as pp


def dice_coefficient(a, b):
    """
    dice coefficient 2nt/na + nb.
    Code taken from https://en.wikibooks.org/wiki/Algorithm_Implementation
    /Strings/Dice%27s_coefficient#Python

    ** Positional Arguments:**
        a:
            - the first array.
        b:
            - the second array.
    """
    a = nar.tolist(nar.flatten(a))
    b = nar.tolist(nar.flatten(b))
    if not len(a) or not len(b):
        return 0.0
    if len(a) == 1:
        a = a + u'.'
    if len(b) == 1:
        b = b + u'.'

    a_bigram_list = []
    for i in range(len(a)-1):
        a_bigram_list.append(a[i:i+2])
    b_bigram_list = []
    for i in range(len(b)-1):
        b_bigram_list.append(b[i:i+2])

    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0/float(len(a_bigrams) + len(b_bigrams))
    return dice_coeff


def mse(imageA, imageB):
    """
    the 'Mean Squared Error' between the two images is the
    sum of the squared difference between the two images;
    NOTE: the two images must have the same dimension
    from http://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
    NOTE: we've normalized the signals by the mean intensity at each
    point to make comparisons btwn fMRI and MPRAGE more viable.
    Otherwise, fMRI signal vastly overpowers MPRAGE signal and our MSE
    would have very low accuracy (fMRI signal differences >>> actual
    differences we are looking for).

    **Positional Arguments:**
        imageA:
            - the first image.
        imageB:
            - the second image.
    """
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= (float(imageA.shape[0] * imageA.shape[1]))
    return float(err)


def compute_kdes(before, after, steps=1000):
    """
    A function to plot kdes of the arrays for the similarity between
    the before/reference and after/reference.

    **Positional Arguments:**
        before:
            - a numpy array before an operational step.
        after:
            - a numpy array after an operational step.
    """
    x_min = min(np.nanmin(before), np.nanmin(after))
    x_max = max(np.nanmax(before), np.nanmax(after))
    x_grid = np.linspace(x_min, x_max, steps)
    kdebef = gaussian_kde(before)
    kdeaft = gaussian_kde(after)
    return [x_grid, kdebef.evaluate(x_grid), kdeaft.evaluate(x_grid)]


def hdist(array1, array2):
    """
    A function for computing the hellinger distance between arrays
    1 and 2.

    **Positional Arguments:**
        array1:
            - the first array.
        array2:
            - the second array.
    """
    return np.sqrt(np.sum((np.sqrt(array1) -
                          np.sqrt(array2)) ** 2)) / float(np.sqrt(2))


def jaccard_index(array1, array2):
    """
    A function to compute the degree of overlap between two binarized
    arrays. Assumes that inputs are already appropriately thresholded,
    and are of the desired shape.

    **Positional Arguments:**
        array1:
            - the first array.
        array2:
            - the second array.
    """
    # binarize if not already
    array1[array1 > 0] = 1
    array1[array1 <= 0] = 0
    array2[array2 > 0] = 1
    array2[array2 <= 0] = 0

    if array1.shape != array2.shape:
        raise ValueError("Your overlap arrays are not the same shape.")
    # definition of the jaccard index is |(A & B)|/|(A | B)|
    overlap = np.logical_and(array1, array2)
    occupied_space = np.logical_or(array1, array2)
    return overlap.sum()/float(occupied_space.sum())


def registration_score(aligned_func, reference, edge=False):
    """
    A function to compute the registration score between two images.

    **Positional Arguments:**
        aligned_func:
            - the brain being aligned. assumed to be a 4d fMRI scan that has
              been masked.
        reference:
            - the template being aligned to. assumed to be a 3d brain or mask.
        edge:
            - whether to plot the edges or not.
    """
    func_name = mgu.get_filename(aligned_func)

    func = nb.load(aligned_func)
    ref = nb.load(reference)
    fid = mgu.get_filename(aligned_func)

    fdat = func.get_data()
    rdat = ref.get_data()

    if fdat.ndim == 4:
        # if our data is 4d, mean over the temporal dimension
        fdat = fdat.mean(axis=3)

    # plot overlay of the thing being aligned with the reference,
    # using the edge-detection algorithm if desired
    freg_qual = plot_overlays(fdat, rdat, edge=edge)
    # compute jaccard index
    reg_score = jaccard_index(fdat, rdat)
    return (reg_score, freg_qual)


def plot_signals(signals, labels, title=None, xlabel=None,
                 ylabel=None, xax=None, lab_incl=True,
                 lwidth=3.0):
    """
    A utility to plot and return a figure for
    multiple signals.

    **Positional Arguments:**

        - signals:
            - a list of the signals you want to have plotted.
        - labels:
            - a list of the labels associated with each signal.
        - title:
            - the title.
        - xlabel:
            - the x label.
        - ylabel:
            - the y label.
        - xax:
            - the scale for the x axis.
        - lab_incl:
            - whether to include the labels on the plot.
        - lwidth:
            - the line width.
    """
    fig_sig = plt.figure()
    ax_sig = fig_sig.add_subplot(111)
    lines = []
    legs = []
    # iterate over the signals and the labels
    for (signal, label) in zip(signals, labels):
        # if we have an x axis, use it, otherwise just use
        # range(0, ... end) which is the default behavior
        if xax is not None:
            lines.append(ax_sig.plot(xax, signal, linewidth=lwidth)[0])
        else:
            lines.append(ax_sig.plot(signal, linewidth=lwidth)[0])
        legs.append(label)  # add the label to our legend
    if lab_incl:
        # if we want to include labels, then plot them
        ax_sig.legend(lines, legs, loc='lower right')
    ax_sig.set_title(title)
    ax_sig.set_ylabel(ylabel)
    ax_sig.set_xlabel(xlabel)
    fig_sig.tight_layout()
    return fig_sig


def plot_timeseries(timeseries, fname_ts, sub, label_name):
    """
    A function to generate a plot of the timeseries
    of the particular ROI. Makes sure nothing nonsensical is
    happening here.

    **Positional Arguments:**
        - timeseries:
            - the path to a roi timeseries.
        - qcdir:
            - the directory to place quality control figures.
    """
    fts_list = []

    # iterate over the roi timeseries to plot a line for each
    # roi
    for d in range(0, timeseries.T.shape[1]):
        fts_list.append(py.graph_objs.Scatter(
                        x=range(0, timeseries.T.shape[0]),
                        y=timeseries.T[:, d], mode='lines'))
    # use plotly so that users can select which rois to display
    # easily with a html
	layout = dict(title="Functional Timeseries, {} Parcellation".format(label_name),
                  xaxis=dict(title='Time Point (TRs)',
                             range=[0, timeseries.T.shape[0]]),
                  yaxis=dict(title='Intensity'),
                  showlegend=False)  # height=405, width=720)
    fts = dict(data=fts_list, layout=layout)
    offline.plot(fts, filename=fname_ts, auto_open=False)
    pass

def plot_connectome(connectome, fname_corr, sub, label_name):
    """
    A function to generate a plot of the timeseries
    of the particular ROI. Makes sure nothing nonsensical is
    happening here.

    **Positional Arguments:**
        - timeseries:
            - the path to a roi timeseries.
        - qcdir:
            - the directory to place quality control figures.
    """
    # plot correlation matrix as the absolute correlation
    # of the timeseries for each roi
    dims = connectome.shape[0]
    fig = pp.plot_heatmap(connectome/np.max(connectome),
        name = "Functional Connectome, {} Parcellation".format(label_name),
        scale = True, scaletit='Normalized Rank')
    fig.layout['xaxis']['title'] = 'ROI'
    fig.layout['yaxis']['title'] = 'ROI'
    fig.layout['yaxis']['autorange'] = 'reversed'
    fig.layout['xaxis']['tickvals'] = [0, dims/2-1, dims-1]
    fig.layout['yaxis']['tickvals'] = [0, dims/2-1, dims-1]
    fig.layout['xaxis']['ticktext'] = [1, dims/2, dims]
    fig.layout['yaxis']['ticktext'] = [1, dims/2, dims]
    offline.plot(fig, filename=fname_corr, auto_open=False)
    pass
