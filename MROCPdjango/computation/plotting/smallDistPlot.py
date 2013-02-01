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


def plotInvDist(invDir, pngName, numBins =100, char = 'class'):
  subj_types,vzero_type, one_type, two_type = csvtodict(char = char) # load up subject types

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
  fig_gl.tight_layout()

  for idx, drcty in enumerate (invDirs):
    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        #arr = np.log(arr)
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

      if idx+1 == 3:
        ax.set_yticks(scipy.arange(0,12,2))
      if idx+1 == 4:
        ax.set_yticks(scipy.arange(0,15,3))
        ax.set_xticks(scipy.arange(0,5,1))

      # Interpolation
      f = interpolate.interp1d(bins, n, kind='cubic')

      x = np.arange(bins[0],bins[-1],0.03) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      plot_color = pickprintcolor(subj_types, arrfn)

      pl.plot(x, interp*100, color = plot_color, linewidth=1)

    if idx == 0:
      pl.ylabel('Percent')
      pl.xlabel('Log Number of Local Triangles')
    if idx == 1:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Local Clustering Coefficient')
    if idx == 2:
      pl.ylabel('Percent')
      pl.xlabel('Log Scan Statistic 1')
    if idx == 3:
      #pl.ylabel('Probability') #**
      pl.xlabel('Log Degree')

  ''' Eigenvalues '''
  ax = pl.subplot(3,2,5)
  #ax.set_yticks(scipy.arange(0,16,4))
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
    pl.xlabel('Eigenvalue rank')

  ''' Global Edges '''
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
    if subj_types[key] == '0':
      zeros.append(ass_ray[key])
    if subj_types[key] == '1':
      ones.append(ass_ray[key])
    if subj_types[key] == '2':
      twos.append(ass_ray[key])

  for cnt, arr in enumerate ([zeros, ones]): #, twos, ass_ray.values()
    pl.figure(1)
    n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
             bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
             rwidth=None, log=False, color=None, label=None, hold=None)

    n = np.append(n,0)

    fig = pl.figure(2)
    ax = pl.subplot(3,2,6)
    ax.set_xticks(scipy.arange(800,1250,200))
    ax.set_yticks(scipy.arange(0,16,4))

    f = interpolate.interp1d(bins, n, kind='cubic')
    x = np.arange(bins[0],bins[-1],0.01) # vary linspc

    interp = f(x)
    ltz = interp < 0
    interp[ltz] = 0

    if cnt == 0: # zeros
      plot_color = 'grey'
    if cnt == 1: # ones
      plot_color = 'blue'
    if cnt == 2:# twos
      plot_color = 'green'
    if cnt == 3: # ALL
      plot_color = 'red'

    pl.plot(x, interp,color = plot_color ,linewidth=1)

  pl.ylabel('Frequency')
  pl.xlabel('Log Global Edge Number')

  caption = 'Six invariants '

  pl.savefig(pngName+'.pdf')
  print '~**** FIN ****~'


def plotstdmean(invDir, pngName, char, numBins =100, function = 'mean'):
  charDict, zero_type, one_type, two_type = csvtodict(char = char)

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
  fig_gl.tight_layout()

  #*********** Start comment here for plot _2 *******#
  for idx, drcty in enumerate (invDirs):

    #matricesArray = assembleAggMatrices(glob(os.path.join(invDir, drcty,'*.npy')), charDict, function, char, 70)
    #processingArrs = perfOpOnMatrices(matricesArray, function, True)

    allmat = np.zeros(shape=(len(charDict),70)); allcnt = 0
    zeromat = np.zeros(shape=(len(zero_type),70)) ; zerocnt = 0
    onemat = np.zeros(shape=(len(one_type),70)); onecnt = 0

    if char == 'class':
      twomat = np.zeros(shape=(len(two_type),70)); twocnt = 0

    for arrfn in glob(os.path.join(invDir, drcty,'*.npy')):
      try:
        arr = np.load(arrfn)
        print "Processing %s..., length --> %d" % (arrfn, len(arr))
      except:
        print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

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

    # Mean of non-zero elements
    if function == 'mean':
      allmatFunc_nnz = allmat.mean(axis=0)[allmat.mean(axis=0).nonzero()]
      zeromatFunc_nnz = zeromat.mean(axis=0)[zeromat.mean(axis=0).nonzero()]
      onematFunc_nnz = onemat.mean(axis=0)[onemat.mean(axis=0).nonzero()]
    elif function == 'stddev':
      allmatFunc_nnz = allmat.std(axis=0)[allmat.std(axis=0).nonzero()]
      zeromatFunc_nnz = zeromat.std(axis=0)[zeromat.std(axis=0).nonzero()]
      onematFunc_nnz = onemat.std(axis=0)[onemat.std(axis=0).nonzero()]

    # Take the log of the mean for clarity
    processingArrs = [np.log(allmatFunc_nnz), np.log(zeromatFunc_nnz), np.log(onematFunc_nnz)]

    if char == 'class':
      if function == 'mean':
        twomatFunc_nnz = twomat.mean(axis=0)[twomat.mean(axis=0).nonzero()]
      elif function == 'stddev':
        twomatFunc_nnz = twomat.std(axis=0)[twomat.std(axis=0).nonzero()]
      processingArrs.append(np.log(twomatFunc_nnz))

    #############################################
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

      fig = pl.figure(2)
      fig.subplots_adjust(hspace=.6)

      ax = pl.subplot(nrows,ncols,(idx*ncols)+2) if proccCnt > 0 else pl.subplot(nrows,ncols,(idx*ncols)+1)

      if proccCnt == 0: # All
        plot_color = 'red'
      if proccCnt == 1: # zero
        plot_color = 'grey'
      if proccCnt == 2: # one
        plot_color = 'blue'
      if proccCnt == 3: # two
        plot_color = 'green'
      # How to plot index
      if function == 'mean':
        pl.plot(x, interp*100, color = plot_color, linewidth=1)
      elif function == 'stddev':
        pl.plot(x, interp, color = plot_color, linewidth=1)

      if idx == 0:
        if function == 'mean':
          ax.set_yticks(scipy.arange(0,7,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.07,0.02))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel(funcVal +' Log # of Local Triangles')
        else:
          pl.xlabel(funcVal +' Log # Triangles by '+ charVal)

      if idx == 1:
        if function == 'mean':
          ax.set_yticks(scipy.arange(0,10,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.15,0.03))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel(funcVal + ' Log Local Clustering Coefficient')
        else:
          pl.xlabel(funcVal + ' Log Local Clustering Coefficient by '+ charVal)

      if idx == 2:
        if function == 'mean':
          ax.set_yticks(scipy.arange(0,8,2))
        elif function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.08,0.02))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel(funcVal + ' Log Scan Statistic 1')
        else:
          pl.xlabel(funcVal + ' Log Scan Statistic 1 by '+ charVal)

      if idx == 3:
        if function == 'mean':
          ax.set_yticks(scipy.arange(0,6,2))
        if function == 'stddev':
          ax.set_yticks(scipy.arange(0,0.08,0.02))
          ax.set_xticks(scipy.arange(-2.5,2.0,1.0))
        if proccCnt == 0:
          if function == 'mean':
            pl.ylabel('Percent')
          elif function == 'stddev':
            pl.ylabel('Magnitude')
          pl.xlabel(funcVal + ' Log Degree')
        else:
          pl.xlabel(funcVal + ' Log Degree by '+ charVal)

  #*********** End comment here for plot _2 *******#

  #*********** Start comment here for plot _1 *******#
  ######## Global Edge number #######

  #arrfn = os.path.join(invDir, 'Globals/numEdgesDict.npy')
  #try:
  #  ass_ray = np.load(arrfn).item() # associative array
  #  print "Processing %s..." % arrfn
  #except:
  #  print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)
  #
  #zeros = []
  #ones = []
  #twos = []
  #
  #for key in ass_ray.keys():
  #  if charDict[key] == '0':
  #    zeros.append(ass_ray[key])
  #  if charDict[key] == '1':
  #    ones.append(ass_ray[key])
  #  if charDict[key] == '2':
  #    twos.append(ass_ray[key])
  #
  #processingArrs = [ass_ray.values(), zeros, ones]
  #if char == 'class':
  #  processingArrs.append(twos)
  #
  #for cnt, arr in enumerate (processingArrs):
  #  pl.figure(1)
  #  n, bins, patches = pl.hist(arr, bins=10 , range=None, normed=False, weights=None, cumulative=False, \
  #           bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
  #           rwidth=None, log=False, color=None, label=None, hold=None)
  #
  #  n = np.append(n,0)
  #
  #  #pl.figure(2)
  #  fig = pl.figure(2)
  #  fig.subplots_adjust(hspace=.5)
  #
  #  ax = pl.subplot(nrows,ncols,1) if cnt == 0 else pl.subplot(nrows,ncols,2)
  #  if cnt == 0:
  #    pl.ylabel('Frequency')
  #    pl.xlabel('Log Global Edge Number')
  #    ax.set_yticks(scipy.arange(0,31,10))
  #  else:
  #    pl.xlabel('Log Global Edge Number by '+ charVal)
  #    ax.set_yticks(scipy.arange(0,15,3))
  #
  #  ax.set_xticks(scipy.arange(800,1250,200))
  #
  #
  #  f = interpolate.interp1d(bins, n, kind='cubic')
  #  x = np.arange(bins[0],bins[-1],0.01) # vary linspc
  #
  #  interp = f(x)
  #  ltz = interp < 0
  #  interp[ltz] = 0
  #
  #  if cnt == 0: # ALL
  #    plot_color = 'red'
  #  if cnt == 1: # zeros
  #    plot_color = 'grey'
  #  if cnt == 2: # ones
  #    plot_color = 'blue'
  #  if cnt == 3:# twos
  #    plot_color = 'green'
  #
  #  pl.plot(x, interp,color = plot_color ,linewidth=1)
  #
  ##### Eigenvalues ####
  #
  #allmat = np.zeros(shape=(len(charDict),68)); allcnt = 0
  #zeromat = np.zeros(shape=(len(zero_type),68)) ; zerocnt = 0
  #onemat = np.zeros(shape=(len(one_type),68)); onecnt = 0
  #if char == 'class':
  #  twomat = np.zeros(shape=(len(two_type),68)); twocnt = 0
  #
  #for arrfn in glob(os.path.join(invDir, EigDir,"*.npy")):
  #  try:
  #    eigv = np.load(arrfn)
  #  except:
  #    print "Eigenvalue array"
  #
  #  n = len(eigv)
  #  arr = (np.sort(eigv)[::-1])
  #
  #  allmat[allcnt] = arr
  #  allcnt += 1
  #
  #  # Populate each matrix by characterization
  #  if charDict[root(arrfn)] == '0':
  #    zeromat[zerocnt]  = arr
  #    zerocnt += 1
  #
  #  elif charDict[root(arrfn)] == '1':
  #    onemat[onecnt] = arr
  #    onecnt += 1
  #
  #  if char == 'class':
  #    if charDict[root(arrfn)] == '2':
  #      twomat[twocnt] = arr
  #      twocnt += 1
  #
  #if function == 'mean':
  #  allmatFunc_nnz = allmat.mean(axis=0)[allmat.mean(axis=0).nonzero()]
  #  zeromatFunc_nnz = zeromat.mean(axis=0)[zeromat.mean(axis=0).nonzero()]
  #  onematFunc_nnz = onemat.mean(axis=0)[onemat.mean(axis=0).nonzero()]
  #elif function == 'stddev':
  #  allmatFunc_nnz = allmat.std(axis=0)[allmat.std(axis=0).nonzero()]
  #  zeromatFunc_nnz = zeromat.std(axis=0)[zeromat.std(axis=0).nonzero()]
  #  onematFunc_nnz = onemat.std(axis=0)[onemat.std(axis=0).nonzero()]
  #
  #processingArrs = [allmatFunc_nnz, zeromatFunc_nnz, onematFunc_nnz]
  #
  #if char == 'class':
  #  if function == 'mean':
  #    twomatFunc_nnz = twomat.mean(axis=0)[twomat.mean(axis=0).nonzero()]
  #  if function == 'stddev':
  #    twomatFunc_nnz = twomat.std(axis=0)[twomat.std(axis=0).nonzero()]
  #  processingArrs.append(twomatFunc_nnz)
  #
  #
  #for proccCnt, arr in enumerate (processingArrs):
  #  if proccCnt == 0: # All
  #    plot_color = 'red'
  #  if proccCnt == 1: # zero
  #    plot_color = 'grey'
  #  if proccCnt == 2: # one
  #    plot_color = 'blue'
  #  if proccCnt == 3: # two
  #    plot_color = 'green'
  #    print 'picking green'
  #
  #  fig = pl.figure(2)
  #  fig.subplots_adjust(hspace=.6)
  #
  #  ax = pl.subplot(nrows,ncols,3) if proccCnt == 0 else pl.subplot(nrows,ncols, 4)
  #  if function == 'mean':
  #    ax.set_yticks(scipy.arange(-0.2,0.2,0.1))
  #    pl.plot(range(1,len(arr)+1), arr/10000, color=plot_color)
  #  elif function == 'stddev':
  #    ax.set_yticks(scipy.arange(0,35,10))
  #    pl.plot(range(1,len(arr)+1), arr/10, color=plot_color)
  #
  #  if proccCnt == 0:
  #    pl.xlabel(funcVal +' Eigenvalue rank')
  #    if function == 'mean':
  #      pl.ylabel('Magnitude ($X 10^4$) ')
  #    elif function == 'stddev':
  #      pl.ylabel('Magnitude ($X 10$) ')
  #  else:
  #    pl.xlabel(funcVal +' Eigenvalue rank by ' + charVal)
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

def assembleAggMatrices(drctyArray, charDict, char, matRowLen):

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
        print "SERIOUS ERROR! THIS SHOULD NEVER HAPPEN!"

      if len(arr) < matRowLen:
        #Pad array with zeros
        arr = np.append(arr, np.zeros(matRowLen - len(arr)))

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
      return [allmat, zeromat, onemat, twomat]
    if char == 'gender':
      return [allmat, zeromat, onemat]

#########################################
#########################################

def perfOpOnMatrices(matricesArray, function, takeLog):
    # Mean of non-zero elements
    processingArrs = []
    for mat in matricesArray:
      if function == 'mean':
        mat_nnz = allmat.mean(axis=0)[allmat.mean(axis=0).nonzero()]
      elif function == 'stddev':
        mat_nnz = allmat.std(axis=0)[allmat.std(axis=0).nonzero()]
      processingArrs.append(mat_nnz)

    # For visualization take the log of the numbers in some cases
    if takeLog == True:
      for idx, mat_nnz in enumerate(processingArrs):
        processingArrs[idx] = np.log(mat_nnz)

    return processingArrs

#########################################
#########################################
#########################################


def main():

    parser = argparse.ArgumentParser(description='Plot distribution of invariant arrays of several graphs')
    parser.add_argument('invDir', action='store',help='The full path of directory containing .npy invariant arrays')
    parser.add_argument('pngName', action='store', help='Full path of directory of resulting png file')
    parser.add_argument('numBins', type = int, action='store', help='Number of bins')
    parser.add_argument('char', action='store', help='Characteristic on which to partition data: gender or class')

    result = parser.parse_args()

    #plotInvDist(result.invDir, result.pngName, result.numBins, result.char)
    #plotstdmean(result.invDir, result.pngName, "gender", result.numBins)
    #func(result.invDir)
    plotstdmean(result.invDir, result.pngName, result.char, result.numBins, function = 'mean') # !!!! NOTE HARDCODE!!!! #

if __name__ == '__main__':
  main()
  #csvtodict(sys.argv[1])
