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

##########################################################################
###########################################################################

def newPlotStdMean(invDir, pngName, char, numBins =100, function = 'mean', numLCCVerticesfn = None):

  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen/values"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]

  print "function =" + function

  charVal = 'Classification' if char == 'class' else 'Gender'
  funcVal = '$\mu$' if function == 'mean' else '$\sigma$'

  nrows = 3
  ncols=2

  if not numLCCVerticesfn:
    matDimZero = 70
  else:
    matDimZero = getMaxVertices(numLCCVerticesfn)
    print "Max dimension --> ", matDimZero

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=nrows, ncols=ncols)
  #fig_gl.tight_layout()

  for idx, drcty in enumerate (invDirs):

    matricesArray = assembleAggMatrices(glob(os.path.join(invDir, drcty,'*.npy')), char, matDimZero)
    processingArrs = perfOpOnMatrices(matricesArray, function, True)



    for proccCnt, arr in enumerate (processingArrs):
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      if numLCCVerticesfn:
        x = np.arange(bins[0],bins[-1],0.03) # vary linspc
      else:
        x = np.arange(bins[0],bins[-1],0.07) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.6)

      #ax = pl.subplot(nrows,ncols,(idx*ncols)+2) if proccCnt > 0 else pl.subplot(nrows,ncols,(idx*ncols)+1)
      ax = pl.subplot(nrows,ncols,idx+1)

      plot_color = getPlotColor(proccCnt, allmat = False)

      if function == 'mean':
        pl.plot(x, interp*100, color = plot_color, linewidth=1)
      elif function == 'stddev':
        pl.plot(x, interp, color = plot_color, linewidth=1)

      if idx == 0:
        if function == 'mean':
          if numLCCVerticesfn:
            pass
            #plt.axis([0, 35, 0, 0.04])
            #ax.set_yticks(scipy.arange(0,0.04,0.01))
          else:
            ax.set_yticks(scipy.arange(0,7,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.07,0.02))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel('Log Number of Local Triangles')
        else:
          pl.xlabel('Log Number of Triangles')

      if idx == 1:
        if function == 'mean':
          if numLCCVerticesfn:
            #ax.set_yticks(scipy.arange(0,0.03,0.01))
            pass
          else:
            ax.set_yticks(scipy.arange(0,10,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.15,0.03))

        pl.xlabel('Log Local Clustering Coefficient')

      if idx == 2:
        if function == 'mean':
          if numLCCVerticesfn:
            pass
            #ax.set_yticks(scipy.arange(0,0.03,0.01))
          else:
            ax.set_yticks(scipy.arange(0,8,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.08,0.02))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')

        pl.xlabel('Log Scan_1 Statistic')

      if idx == 3:
        if function == 'mean':
          if numLCCVerticesfn:
            pass
            #ax.set_yticks(scipy.arange(0,0.04,0.01))
          else:
            ax.set_yticks(scipy.arange(0,6,2))
        if function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.08,0.02))
          ax.set_xticks(scipy.arange(-2.5,2.0,1.0))

        pl.xlabel('Log Degree')

  #### Eigenvalues ####

  if not numLCCVerticesfn:
    numEigs = 68
  else:
    numEigs = 100

  ax = pl.subplot(nrows,ncols,5)
  matricesArray = assembleAggMatrices(glob(os.path.join(invDir, EigDir,'*.npy')), char, numEigs, eig = True)
  processingArrs = perfOpOnMatrices(matricesArray, function, False)

  for proccCnt, arr in enumerate (processingArrs):
    plot_color = getPlotColor(proccCnt, allmat = False)

    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.6)

    if function == 'mean':
      if numLCCVerticesfn:
        pass
      else:
        ax.set_yticks(scipy.arange(-0.2,0.2,0.1))
      pl.plot(range(1,len(arr)+1), arr/10000, color=plot_color)
    elif function == 'stddev':
      ax.set_yticks(scipy.arange(0,35,10))
      pl.plot(range(1,len(arr)+1), arr/10, color=plot_color)

  pl.xlabel('Eigenvalue rank')
  if function == 'mean':
    pl.ylabel('Magnitude x $10^4$ ')
  elif function == 'stddev':
    pl.ylabel('Magnitude x $ 10$ ')

  pl.xlabel('Eigenvalue rank')

  ######## Global Edge number #######

  charDict, zero_type, one_type, two_type = csvtodict(char = char)
  ax = pl.subplot(nrows,ncols,6)

  arrfn = os.path.join(invDir, 'Globals/numEdgesDict.npy')
  try:
    ass_ray = np.load(arrfn).item() # associative array
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

  zeros = []
  ones = []
  twos = []

  for key in ass_ray.keys():
    if charDict[key] == '0':
      zeros.append(ass_ray[key])
    if charDict[key] == '1':
      ones.append(ass_ray[key])
    if charDict[key] == '2':
      twos.append(ass_ray[key])

  processingArrs = [zeros, ones]
  if char == 'class':
    processingArrs.append(twos)

  for proccCnt, arr in enumerate (processingArrs):
    pl.figure(1)

    arr = np.log(np.array(arr)[np.array(arr).nonzero()]) # NOTE THIS CHANGE

    n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)
    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.5)

    pl.ylabel('Frequency')

    pl.xlabel('Log Global Edge Number')
    if numLCCVerticesfn:
      pass
    else:
      #ax.set_yticks(scipy.arange(0,15,3))
      #ax.set_xticks(scipy.arange(800,1250,200))
      pass

    f = interpolate.interp1d(bins, n, kind='cubic')
    x = np.arange(bins[0],bins[-1],0.01) # vary linspc

    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0

    plot_color = getPlotColor(proccCnt, allmat = False)
    pl.plot(x, interp,color = plot_color ,linewidth=1)

  pl.savefig(pngName+'.pdf')
  print '~**** Done  ****~'

##########################################################################
###########################################################################

def newPlotErrStdMean(invDir, pngName, char, numBins =100, function = 'mean'):

  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen/values"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]

  print "function =" + function

  charVal = 'Classification' if char == 'class' else 'Gender'
  funcVal = '$\mu$' if function == 'mean' else '$\sigma$'

  nrows = 3
  ncols=2

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=nrows, ncols=ncols)
  #fig_gl.tight_layout()

  for idx, drcty in enumerate (invDirs):

    matricesArray = assembleAggMatrices(glob(os.path.join(invDir, drcty,'*.npy')), char, 70)
    processingArrs = perfOpOnMatrices(matricesArray, function, True)

    stddevArrs = perfOpOnMatrices(matricesArray, 'stddev', True)


    for proccCnt, arr in enumerate (processingArrs):
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      x = np.arange(bins[0],bins[-1],0.07) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      # Do the same for stddev values

      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      stdx = np.arange(bins[0],bins[-1],0.07) # vary linspc

      stdinterp = f(x)
      ltz = interp < 0
      stdinterp[ltz] = 0

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.6)

      #ax = pl.subplot(nrows,ncols,(idx*ncols)+2) if proccCnt > 0 else pl.subplot(nrows,ncols,(idx*ncols)+1)
      ax = pl.subplot(nrows,ncols,idx+1)

      if proccCnt == 0: # zero
        plot_color = 'grey'
        label = 'male'
      if proccCnt == 1: # one
        plot_color = 'blue'
        label = 'female'
      if proccCnt == 2: # two
        plot_color = 'green'

      ax.errorbar(x, interp*100, yerr = stdinterp, color='green')

      if idx == 1:
        pl.plot(x, interp*100, color = plot_color, linewidth=1, label=label)
        plt.legend(bbox_to_anchor=(0.7, 1.3), loc=2, prop={'size':8}, borderaxespad=0.)
	#plt.legend().draw_frame(False)
      else:
        pl.plot(x, interp*100, color = plot_color, linewidth=1)

      if idx == 0:
        ax.set_yticks(scipy.arange(0,7,2))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel(funcVal +' Log # of Local Triangles')
        else:
          pl.xlabel(funcVal +' Log # Triangles')

      if idx == 1:
        ax.set_yticks(scipy.arange(0,12,3))
        pl.xlabel(funcVal + ' Log Local Clustering Coefficient')

      if idx == 2:
        ax.set_yticks(scipy.arange(0,8,2))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')

        pl.xlabel(funcVal + ' Log Scan Statistic 1')

      if idx == 3:
        ax.set_yticks(scipy.arange(0,6,2))
        pl.xlabel(funcVal + ' Log Degree')

  #### Eigenvalues ####

  ax = pl.subplot(nrows,ncols,5)
  matricesArray = assembleAggMatrices(glob(os.path.join(invDir, EigDir,'*.npy')), char, 68, eig = True)
  processingArrs = perfOpOnMatrices(matricesArray, function, False)

  for proccCnt, arr in enumerate (processingArrs):
    plot_color = getPlotColor(proccCnt, allmat = False)

    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.6)

    if function == 'mean':
      ax.set_yticks(scipy.arange(-0.2,0.2,0.1))
      pl.plot(range(1,len(arr)+1), arr/10000, color=plot_color)
    elif function == 'stddev':
      ax.set_yticks(scipy.arange(0,35,10))
      pl.plot(range(1,len(arr)+1), arr/10, color=plot_color)

  pl.xlabel(funcVal +' Eigenvalue rank')
  if function == 'mean':
    pl.ylabel('Magnitude x $10^4$ ')
  elif function == 'stddev':
    pl.ylabel('Magnitude x $10$ ')

  pl.xlabel( funcVal +' Eigenvalue rank')

  ######## Global Edge number #######
  charDict, zero_type, one_type, two_type = csvtodict(char = char)
  ax = pl.subplot(nrows,ncols,6)

  arrfn = os.path.join(invDir, 'Globals/numEdgesDict.npy')
  try:
    ass_ray = np.load(arrfn).item() # associative array
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

  zeros = []
  ones = []
  twos = []

  for key in ass_ray.keys():
    if charDict[key] == '0':
      zeros.append(ass_ray[key])
    if charDict[key] == '1':
      ones.append(ass_ray[key])
    if charDict[key] == '2':
      twos.append(ass_ray[key])

  processingArrs = [zeros, ones]
  if char == 'class':
    processingArrs.append(twos)

  for proccCnt, arr in enumerate (processingArrs):
    pl.figure(1)
    n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)
    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.5)

    pl.ylabel('Frequency')

    pl.xlabel('Log Global Edge Number')
    ax.set_yticks(scipy.arange(0,15,3))
    ax.set_xticks(scipy.arange(800,1250,200))

    f = interpolate.interp1d(bins, n, kind='cubic')
    x = np.arange(bins[0],bins[-1],0.01) # vary linspc

    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0

    plot_color = getPlotColor(proccCnt, allmat = False)
    pl.plot(x, interp,color = plot_color ,linewidth=1)

  pl.savefig(pngName+'.pdf')
  print '~**** Done  ****~'


############################################################################
############################################################################



def getPlotColor(proccCnt, allmat = True):
  if allmat:
    if proccCnt == 0: # All
      return 'red'
    if proccCnt == 1: # zero
      return 'grey'
    if proccCnt == 2: # one
      return 'blue'
    if proccCnt == 3: # two
      return 'green'
  else:
    if proccCnt == 0: # zero
      return 'grey'
    if proccCnt == 1: # one
      return 'blue'
    if proccCnt == 2: # two
      return 'green'

############################################################################
############################################################################

def plotstdmean(invDir, pngName, char, numBins =100, function = 'mean'):
  #charDict, zero_type, one_type, two_type = csvtodict(char = char)

  print "function =" + function

  charVal = 'Classification' if char == 'class' else 'Gender'
  funcVal = '$\mu$' if function == 'mean' else '$\sigma$'

  # ClustCoeff  Degree  Eigen  MAD  numEdges.npy  ScanStat  Triangle
  MADdir = "MAD"
  ccDir = "ClustCoeff"
  DegDir = "Degree"
  EigDir = "Eigen/values"
  SS1dir = "ScanStat1"
  triDir = "Triangle"

  invDirs = [triDir, ccDir, SS1dir, DegDir ]
  nrows=4
  ncols=2

  if not os.path.exists(invDir):
    print "%s does not exist" % invDir
    sys.exit(1)

  pl.figure(2)
  fig_gl, axes = pl.subplots(nrows=nrows, ncols=ncols)
  #fig_gl.tight_layout()

  #*********** Start comment here for plot _2 *******#
  #for idx, drcty in enumerate (invDirs):
  #
  #  matricesArray = assembleAggMatrices(glob(os.path.join(invDir, drcty,'*.npy')), char, 70)
  #  processingArrs = perfOpOnMatrices(matricesArray, function, True)
  #
  #  for proccCnt, arr in enumerate (processingArrs):
  #    pl.figure(1)
  #    n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
  #             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
  #             rwidth=None, log=False, color=None, label=None, hold=None)
  #
  #    n = np.append(n,0)
  #    n = n/float(sum(n))
  #
  #    # Interpolation
  #    f = interpolate.interp1d(bins, n, kind='cubic')
  #
  #    x = np.arange(bins[0],bins[-1],0.07) # vary linspc
  #
  #    interp = f(x)
  #    ltz = interp < 0
  #    interp[ltz] = 0
  #
  #    fig = pl.figure(2)
  #    fig.subplots_adjust(hspace=.6)
  #
  #    ax = pl.subplot(nrows,ncols,(idx*ncols)+2) if proccCnt > 0 else pl.subplot(nrows,ncols,(idx*ncols)+1)
  #
  #    if proccCnt == 0: # All
  #      plot_color = 'red'
  #    if proccCnt == 1: # zero
  #      plot_color = 'grey'
  #    if proccCnt == 2: # one
  #      plot_color = 'blue'
  #    if proccCnt == 3: # two
  #      plot_color = 'green'
  #    # How to plot index
  #    if function == 'mean':
  #      pl.plot(x, interp*100, color = plot_color, linewidth=1)
  #    elif function == 'stddev':
  #      pl.plot(x, interp, color = plot_color, linewidth=1)
  #
  #    if idx == 0:
  #      if function == 'mean':
  #        ax.set_yticks(scipy.arange(0,7,2))
  #      elif function == 'stddev':
  #        ax.set_yticks(scipy.arange(0,0.07,0.02))
  #      if proccCnt == 0:
  #        if function == 'mean':
  #          pl.ylabel('Percent')
  #        elif function == 'stddev':
  #          pl.ylabel('Magnitude')
  #        pl.xlabel(funcVal +' Log # of Local Triangles')
  #      else:
  #        pl.xlabel(funcVal +' Log # Triangles by '+ charVal)
  #
  #    if idx == 1:
  #      if function == 'mean':
  #        ax.set_yticks(scipy.arange(0,10,2))
  #      elif function == 'stddev':
  #        ax.set_yticks(scipy.arange(0,0.15,0.03))
  #      if proccCnt == 0:
  #        if function == 'mean':
  #          pl.ylabel('Percent')
  #        elif function == 'stddev':
  #          pl.ylabel('Magnitude')
  #        pl.xlabel(funcVal + ' Log Local Clustering Coefficient')
  #      else:
  #        pl.xlabel(funcVal + ' Log Local Clustering Coefficient by '+ charVal)
  #
  #    if idx == 2:
  #      if function == 'mean':
  #        ax.set_yticks(scipy.arange(0,8,2))
  #      elif function == 'stddev':
  #        ax.set_yticks(scipy.arange(0,0.08,0.02))
  #      if proccCnt == 0:
  #        if function == 'mean':
  #          pl.ylabel('Percent')
  #        elif function == 'stddev':
  #          pl.ylabel('Magnitude')
  #        pl.xlabel(funcVal + ' Log Scan Statistic 1')
  #      else:
  #        pl.xlabel(funcVal + ' Log Scan Statistic 1 by '+ charVal)
  #
  #    if idx == 3:
  #      if function == 'mean':
  #        ax.set_yticks(scipy.arange(0,6,2))
  #      if function == 'stddev':
  #        ax.set_yticks(scipy.arange(0,0.08,0.02))
  #        ax.set_xticks(scipy.arange(-2.5,2.0,1.0))
  #      if proccCnt == 0:
  #        if function == 'mean':
  #          pl.ylabel('Percent')
  #        elif function == 'stddev':
  #          pl.ylabel('Magnitude')
  #        pl.xlabel(funcVal + ' Log Degree')
  #      else:
  #        pl.xlabel(funcVal + ' Log Degree by '+ charVal)

  #*********** End comment here for plot _2 *******#

  #*********** Start comment here for plot _1 *******#
  ######## Global Edge number #######
  charDict, zero_type, one_type, two_type = csvtodict(char = char)
  arrfn = os.path.join(invDir, 'Globals/numEdgesDict.npy')
  try:
    ass_ray = np.load(arrfn).item() # associative array
    print "Processing %s..." % arrfn
  except:
    print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

  zeros = []
  ones = []
  twos = []

  for key in ass_ray.keys():
    if charDict[key] == '0':
      zeros.append(ass_ray[key])
    if charDict[key] == '1':
      ones.append(ass_ray[key])
    if charDict[key] == '2':
      twos.append(ass_ray[key])

  processingArrs = [ass_ray.values(), zeros, ones]
  if char == 'class':
    processingArrs.append(twos)

  for cnt, arr in enumerate (processingArrs):
    pl.figure(1)
    n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)

    #pl.figure(2)
    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.5)

    ax = pl.subplot(nrows,ncols,1) if cnt == 0 else pl.subplot(nrows,ncols,2)
    if cnt == 0:
      pl.ylabel('Frequency')
      pl.xlabel('Log Global Edge Number')
      ax.set_yticks(scipy.arange(0,31,10))
    else:
      pl.xlabel('Log Global Edge Number by '+ charVal)
      ax.set_yticks(scipy.arange(0,15,3))

    ax.set_xticks(scipy.arange(800,1250,200))


    f = interpolate.interp1d(bins, n, kind='cubic')
    x = np.arange(bins[0],bins[-1],0.01) # vary linspc

    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0

    if cnt == 0: # ALL
      plot_color = 'red'
    if cnt == 1: # zeros
      plot_color = 'grey'
    if cnt == 2: # ones
      plot_color = 'blue'
    if cnt == 3:# twos
      plot_color = 'green'

    pl.plot(x, interp,color = plot_color ,linewidth=1)

  ##### Eigenvalues ####

  matricesArray = assembleAggMatrices(glob(os.path.join(invDir, EigDir,'*.npy')), char, 70, eig = True)
  processingArrs = perfOpOnMatrices(matricesArray, function, False)

  for proccCnt, arr in enumerate (processingArrs):
    if proccCnt == 0: # All
      plot_color = 'red'
    if proccCnt == 1: # zero
      plot_color = 'grey'
    if proccCnt == 2: # one
      plot_color = 'blue'
    if proccCnt == 3: # two
      plot_color = 'green'
      print 'picking green'

    fig = pl.figure(2)
    fig.subplots_adjust(hspace=.6)

    ax = pl.subplot(nrows,ncols,3) if proccCnt == 0 else pl.subplot(nrows,ncols, 4)
    if function == 'mean':
      ax.set_yticks(scipy.arange(-0.2,0.2,0.1))
      pl.plot(range(1,len(arr)+1), arr/10000, color=plot_color)
    elif function == 'stddev':
      ax.set_yticks(scipy.arange(0,35,10))
      pl.plot(range(1,len(arr)+1), arr/10, color=plot_color)

    if proccCnt == 0:
      pl.xlabel(funcVal +' Eigenvalue rank')
      if function == 'mean':
        pl.ylabel('Magnitude ($X 10^4$) ')
      elif function == 'stddev':
        pl.ylabel('Magnitude ($X 10$) ')
    else:
      pl.xlabel(funcVal +' Eigenvalue rank by ' + charVal)
  #*********** End comment here for plot _1 *******#

  print 'done'
  pl.savefig(pngName+'.pdf')

#########################################
#########################################
##########################################

def root(arrfn):
  return (arrfn.split('/')[-1]).split('_')[0]

##########################################
##########################################

def func(d):
  charDict, zero_type, one_type = csvtodict(char = 'gender')

  arrDir  = []
  for fn in glob(os.path.join(d,"*")):
    arrDir.append(root(fn))

  for i in charDict.keys():
    if i not in arrDir:
      print i

#########################################
#########################################

def getMaxVertices(globalVertFn):
  vertArr = np.load(globalVertFn).item()
  return np.max(vertArr.values())

#########################################
#########################################

def assembleAggMatrices(drctyArray, char, matRowLen, eig = False):
  charDict, zero_type, one_type, two_type = csvtodict(char = char)

  allmat = np.zeros(shape=(len(charDict),matRowLen)); allcnt = 0
  zeromat = np.zeros(shape=(len(zero_type),matRowLen)) ; zerocnt = 0
  onemat = np.zeros(shape=(len(one_type),matRowLen)); onecnt = 0

  if char == 'class':
    twomat = np.zeros(shape=(len(two_type),matRowLen)); twocnt = 0

  for arrfn in drctyArray:
    try:
      arr = np.load(arrfn)
      print "Processing %s..., length --> %d" % (arrfn, len(arr))
    except:
      print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

    if len(arr) > matRowLen:
      import pdb; pdb.set_trace()
      print "SERIOUS ERROR! THIS SHOULD NEVER HAPPEN!"

    if len(arr) < matRowLen:
      #Pad array with zeros
      arr = np.append(arr, np.zeros(matRowLen - len(arr)))

    if eig:
      n = len(arr)
      arr = (np.sort(arr)[::-1])

    allmat[allcnt] = arr
    allcnt += 1

    # Populate each matrix by characterization
    if charDict[root(arrfn)] == '0':
      zeromat[zerocnt]  = arr
      zerocnt += 1

    elif charDict[root(arrfn)] == '1':
      onemat[onecnt] = arr
      onecnt += 1

    if char == 'class':
      if charDict[root(arrfn)] == '2':
        twomat[twocnt] = arr
        twocnt += 1

  if char == 'class':
    #return [allmat, zeromat, onemat, twomat]
    return [zeromat, onemat, twomat]
  if char == 'gender':
    return [zeromat, onemat]
    #return [allmat, zeromat, onemat]

#########################################
#########################################

def perfOpOnMatrices(matricesArray, function, takeLog):
  # Mean of non-zero elements
  processingArrs = []
  for mat in matricesArray:
    if function == 'mean':
      mat_nnz = mat.mean(axis=0)[mat.mean(axis=0).nonzero()]
    elif function == 'stddev':
      mat_nnz = mat.std(axis=0)[mat.std(axis=0).nonzero()]
    processingArrs.append(mat_nnz)

  # For visualization take the log of the numbers in some cases
  if takeLog == True:
    for idx, mat_nnz in enumerate(processingArrs):
      processingArrs[idx] = np.log(mat_nnz)

  return processingArrs

#########################################
#########################################

def lineno():
  '''
  Get current line number
  '''
  return str(inspect.getframeinfo(inspect.currentframe())[1])

#########################################
#########################################

def csvtodict(fn ='/home/disa/code/mrn_covariates_n120-v4.csv', char = 'class'):
  alldict = {}
  zerosdict = {}
  onesdict = {}
  twosdict = {}

  if char == 'class':
    col = 4
  elif char == 'gender':
    col = 2
  reader = csv.reader(open(fn, 'rb'))

  for row in reader:
    alldict[row[0].strip()] = row[col].strip()

    if row[col].strip() == '0':
      zerosdict[row[0].strip()] = row[col].strip()

    if row[col].strip() == '1':
      onesdict[row[0].strip()] = row[col].strip()

    if row[col].strip() == '2':
      twosdict[row[0].strip()] = row[col].strip()

    #print row[0] ,'TYPE' ,alldict[row[0]]
    #import pdb; pdb.set_trace()

  del alldict ['URSI'] # Header

  return [alldict, zerosdict, onesdict, twosdict]

#########################################
#########################################

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

#########################################
#########################################
#########################################

def main():
  parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
  parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
  parser.add_argument('pngName', action='store', help='Full path of directory of resulting png file')
  parser.add_argument('numBins', type = int, action='store', help='Number of bins')
  parser.add_argument('char', action='store', help='Characteristic on which to partition data: gender or class')

  parser.add_argument('-b', '--big', action='store', help='if working on big graphs pass in numLCCVertices.npy full with this param')

  result = parser.parse_args()

  if result.big:
    plotInvDist(result.invDir, result.pngName, result.numBins, result.char, True)
  else:
    plotInvDist(result.invDir, result.pngName, result.numBins, result.char)

  #plotstdmean(result.invDir, result.pngName, "gender", result.numBins)
  #func(result.invDir)
  #if result.big:
  #  newPlotStdMean(result.invDir, result.pngName, result.char, result.numBins, function = 'mean', numLCCVerticesfn = result.big) # '/mnt/braingraph1data/projects/MR/MRN/invariants/big/Globals/numLCCVerticesDict.npy'
  #plotstdmean(result.invDir, result.pngName, result.char, result.numBins, function = 'mean') # !!!! NOTE HARDCODE!!!! #
  #else:
  #  newPlotStdMean(result.invDir, result.pngName, result.char, result.numBins, function = 'mean')
  #  newPlotErrStdMean(result.invDir, result.pngName, result.char, result.numBins, function = 'mean')

if __name__ == '__main__':
  main()
  #csvtodict(sys.argv[1])