#!/usr/bin/python

# Author: Disa Mhembere, Johns Hopkins University
# Separated: 10/2/2012
# Plot all .np arrays in a common dir on the same axis & save
# 1 indexed

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pylab as pl

import numpy as np
import os
import sys
from glob import glob
import argparse
import scipy
from scipy import interpolate
import inspect
import csv

# Issues: Done nothing with MAD

def lineno():
  '''
  Get current line number
  '''
  return str(inspect.getframeinfo(inspect.currentframe())[1])

def csvtodict(fn ='/home/disa/code/mrn_covariates_n120-v4.csv', char = 'class'):

  if char == 'class':
    col = 4
  elif char == 'gender':
    col = 2
  reader = csv.reader(open(fn, 'rb'))

  outdict = dict()
  for row in reader:
    outdict[row[0].strip()] = row[col].strip()
    #print row[0] ,'TYPE' ,outdict[row[0]]
  #import pdb; pdb.set_trace()
  return outdict


def pickprintcolor(charDict, arrfn):
  '''
  charDict: dict
  '''
  if (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '0'):
    plot_color = 'grey'
  elif (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '1'):
    plot_color = 'blue'
  elif (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '2'):
    plot_color = 'green'
  else:
    print "[ERROR]: %s, no match on subject type" % lineno()

  return plot_color

def plotInvDist(invDir, pngName, numBins =100):
  subj_types = csvtodict(char = 'class') # load up subject types

  # ClustCoeff  Degree  Eigen  MAD  numEdges.npy  ScanStat  Triangle
  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen/values"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=3, ncols=2)

  for idx, drcty in enumerate (invDirs):
    xval = 0;
    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        arr = np.log(arr[arr.nonzero()])
        print "Processing %s..." % arrfn
      except:
        print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.5)

      ax = pl.subplot(3,2,idx+1)

      if idx == 0:
        plt.axis([0, 35, 0, 0.04])
        ax.set_yticks(scipy.arange(0,0.04,0.01))
      if idx == 1 or idx == 2:
        ax.set_yticks(scipy.arange(0,0.03,0.01))
      if idx == 3:
        ax.set_yticks(scipy.arange(0,0.04,0.01))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      x = np.arange(bins[0],bins[-1],0.03) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      plot_color = pickprintcolor(subj_types, arrfn)

      pl.plot(x, interp, color = plot_color, linewidth=1)
      if xval == x:
        print '***Same!***'
      xval = x;

    if idx == 0:
      pl.ylabel('Probability')
      pl.xlabel('Log Number of Local Triangles')
    if idx == 1:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Local Clustering Coefficient')
    if idx == 2:
      pl.ylabel('Probability')
      pl.xlabel('Log Scan Statistic 1')
    if idx == 3:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Degree')

  ''' Eigenvalues '''
  ax = pl.subplot(3,2,5)
  ax.set_yticks(scipy.arange(0,16,4))
  for eigValInstance in glob(os.path.join(invDir, EigDir,"*.npy")):
    try:
      eigv = np.load(eigValInstance)
    except:
      print "Eigenvalue array"

    n = len(eigv)
    sa = (np.sort(eigv)[::-1])

    plot_color = pickprintcolor(subj_types, eigValInstance)

    pl.plot(range(1,n+1), sa/10000, color=plot_color)
    pl.ylabel('Magnitude ($X 10^4$) ')
    pl.xlabel('Eigenvalue Rank')

  ''' Edges '''
  arrfn = os.path.join(invDir, 'Globals/numEdges.npy')
  try:
    arr = np.load(arrfn)
    arr = np.log(arr[arr.nonzero()])
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
  pl.figure(1)
  n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
           bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
           rwidth=None, log=False, color=None, label=None, hold=None)

  n = np.append(n,0)

  fig = pl.figure(2)
  ax = pl.subplot(3,2,6)
  ax.set_xticks(scipy.arange(17.2,18.1,0.2))

  f = interpolate.interp1d(bins, n, kind='cubic')
  x = np.arange(bins[0],bins[-1],0.01) # vary linspc

  interp = f(x)
  ltz = interp < 0
  interp[ltz] = 0
  pl.plot(x, interp,color ='grey' ,linewidth=1)
  pl.ylabel('Frequency')
  pl.xlabel('Log Global Edge Number')

  pl.savefig(pngName+'.pdf')

#################################################
##################################################
##################################################


def plotstdmean(invDir, pngName, numBins =100):
  subj_types = csvtodict() # load up subject types

  # ClustCoeff  Degree  Eigen  MAD  numEdges.npy  ScanStat  Triangle
  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=3, ncols=2)
  fig_gl.tight_layout()

  for idx, drcty in enumerate (invDirs):

    mean_arr = []
    stddev_arr = []

    ones_mean = []
    twos_mean = []
    zeros_mean = []

    ones_std = []
    twos_std = []
    zeros_std = []

    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        arr = np.log(arr[arr.nonzero()])
        print "Processing %s..." % arrfn
      except:
        print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.5)

      nrows=5
      ncols=4

      ax = pl.subplot(nrows,ncols,idx+1)

      if idx == 0:
        plt.axis([0, 35, 0, 0.04])
        ax.set_yticks(scipy.arange(0,0.04,0.01))
      if idx == 1 or idx == 2:
        ax.set_yticks(scipy.arange(0,0.03,0.01))
      if idx == 3:
        ax.set_yticks(scipy.arange(0,0.04,0.01))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      x = np.arange(bins[0],bins[-1],0.03) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      import pdb; pdb.set_trace()

      '''
      pl.plot(x, interp, color = plot_color, linewidth=1)

      if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '0'):
        zeros_mean.append(arr.mean())
        zeros_std.append(arr.std())

      if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '1'):
        ones_mean.append(arr.mean())
        ones_std.append(arr.std())

      if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '2'):
        twos_mean.append(arr.mean())
        twos_std.append(arr.std())
      '''

    plot_color = pickprintcolor(subj_types, arrfn)

    if idx == 0:
      pl.ylabel('Probability')
      pl.xlabel('Log Number of Local Triangles')
    if idx == 1:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Local Clustering Coefficient')
    if idx == 2:
      pl.ylabel('Probability')
      pl.xlabel('Log Scan Statistic 1')
    if idx == 3:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Degree')

  ''' Eigenvalues '''
  ax = pl.subplot(3,2,5)
  ax.set_yticks(scipy.arange(0,16,4))
  for eigValInstance in glob(os.path.join(invDir, EigDir,"*.npy")):
    try:
      eigv = np.load(eigValInstance)
    except:
      print "Eigenvalue array"

    n = len(eigv)
    sa = (np.sort(eigv)[::-1])

    plot_color = pickprintcolor(subj_types, eigValInstance)

    pl.plot(range(1,n+1), sa/10000, color=plot_color)
    pl.ylabel('Magnitude ($X 10^4$) ')
    pl.xlabel('eigenvalue rank')

  ''' Edges '''
  arrfn = os.path.join(invDir, 'Globals/numEdges.npy')
  try:
    arr = np.load(arrfn)
    arr = np.log(arr[arr.nonzero()])
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
  pl.figure(1)
  n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
           bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
           rwidth=None, log=False, color=None, label=None, hold=None)

  n = np.append(n,0)

  fig = pl.figure(2)
  ax = pl.subplot(3,2,6)
  ax.set_xticks(scipy.arange(17.2,18.1,0.2))

  f = interpolate.interp1d(bins, n, kind='cubic')
  x = np.arange(bins[0],bins[-1],0.01) # vary linspc

  interp = f(x)
  ltz = interp < 0
  interp[ltz] = 0
  pl.plot(x, interp,color ='grey' ,linewidth=1)
  pl.ylabel('Frequency')
  pl.xlabel('log global edge number')

  pl.savefig(pngName+'.png')



##################################################
##################################################
##################################################



def OLDplotstdmean(invDir, pngName):
  subj_types = csvtodict() # load up subject types

  # ClustCoeff  Degree  Eigen  MAD  numEdges.npy  ScanStat  Triangle
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]
  #invDirs = []

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(1)

  nrows=4
  ncols=2

  fig_gl, axes = pl.subplots(nrows=nrows, ncols=ncols)
  fig_gl.tight_layout()

  for idx, drcty in enumerate (invDirs):
    mean_arr = []
    stddev_arr = []

    ones_mean = []
    twos_mean = []
    zeros_mean = []

    ones_std = []
    twos_std = []
    zeros_std = []

    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        mean_arr.append(arr.mean())
        stddev_arr.append(arr.std())

        if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '0'):
          zeros_mean.append(arr.mean())
          zeros_std.append(arr.std())

        if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '1'):
          ones_mean.append(arr.mean())
          ones_std.append(arr.std())

        if ( subj_types[arrfn.split('/')[-1].split('_')[0]] == '2'):
          twos_mean.append(arr.mean())
          twos_std.append(arr.std())

        #mean_arr.append(np.log(arr.mean()))
        #stddev_arr.append(np.log(arr.std()))
        #arr = np.log(arr[arr.nonzero()])
        print "Processing %s..." % arrfn
      except:
        print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

    mean_arr = np.array(mean_arr)
    stddev_arr = np.array(stddev_arr)

    ax = pl.subplot(nrows,ncols,(idx*ncols)+1)
    ax.set_yticks(scipy.arange(0,1,.25))
    pl.gcf().subplots_adjust(bottom=0.07)

    '''
    if idx == 0:
      plt.axis([0, 35, 0, 0.04])
      ax.set_yticks(scipy.arange(0,0.04,0.01))
    if idx == 1 or idx == 2:
      ax.set_yticks(scipy.arange(0,0.03,0.01))
    if idx == 3:
      ax.set_yticks(scipy.arange(0,0.04,0.01))
    '''

    # Interpolation
    #f = interpolate.interp1d(bins, n, kind='cubic')

    #x = np.arange(bins[0],bins[-1],0.03) # vary linspc

    #interp = f(x)
    #ltz = interp < 0
    #interp[ltz] = 0

    #plot_color = pickprintcolor(subj_types, arrfn)
    #pl.plot(x, interp, color = plot_color, linewidth=1)

    #pl.plot(mean_arr/float(mean_arr.max()), color = "black", linewidth=1)

    if (idx*ncols)+1 == 1:
      pl.ylabel('')
    pl.xlabel('Norm. Local Triangle Count Mean')
    if (idx*ncols)+1 == 3:
      #pl.ylabel('Probability') #**
      pl.xlabel('Norm. Local Clustering Coefficient Mean')
    if (idx*ncols)+1 == 5:
      pl.ylabel('Normalized Magnitude Scale')
      pl.xlabel('Norm. Scan Statistic 1 Mean')
    if (idx*ncols)+1 == 7:
      #pl.ylabel('Probability') #**
      pl.xlabel('Norm. Local Degree Mean')

    pl.plot(zeros_mean, color = 'grey' , linewidth=1)
    pl.plot(ones_mean, color = 'blue', linewidth=1)
    pl.plot(twos_mean, color = 'green', linewidth=1)

    ax = pl.subplot(nrows,ncols,(idx*ncols)+2)
    ax.set_yticks(scipy.arange(0,1,.25))
    pl.gcf().subplots_adjust(bottom=0.07)


    stddev_arr = np.array(stddev_arr)
    #pl.plot(stddev_arr/float(stddev_arr.max()), color = "black", linewidth=1)
    if (idx*ncols)+2 == 2:
      pl.ylabel('')
      pl.xlabel('Norm. Local Triangle Count Std Dev')
    if (idx*ncols)+2 == 4:
      #pl.ylabel('Probability') #**
      pl.xlabel('Norm. Local Clustering Coefficient Std Dev')
    if (idx*ncols)+2 == 6:
      #pl.ylabel('Probability')
      pl.xlabel('Norm. Scan Statistic 1 Std Dev')
    if (idx*ncols)+2 == 8:
      #pl.ylabel('Probability') #**
      pl.xlabel('Norm. Local Degree Std Dev')

    pl.plot(zeros_std, color = 'grey' , linewidth=1)
    pl.plot(ones_std, color = 'blue', linewidth=1)
    pl.plot(twos_std, color = 'green', linewidth=1)

  pl.savefig(pngName+'.png')


def main():

    parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
    parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
    parser.add_argument('pngName', action='store', help='Full path of directory of resulting png file')
    parser.add_argument('numBins', type = int, action='store', help='Number of bins')

    result = parser.parse_args()

    plotInvDist(result.invDir, result.pngName, result.numBins)
    #plotstdmean(result.invDir, result.pngName)

if __name__ == '__main__':
  main()
  #csvtodict(sys.argv[1])
