import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
import os
from glob import glob
import inspect
import csv
from scipy import interpolate

#########################################
#########################################
##########################################

def root(arrfn):
  return (arrfn.split('/')[-1]).split('_')[0]

#########################################
#########################################

def getMaxVertices(globalVertFn):
  vertArr = np.load(globalVertFn).item()
  return np.max(vertArr.values())

#########################################
#########################################

def assembleAggMatrices(drctyArray, char, matRowLen, numBins = 100, eig = False):
  charDict, zero_type, one_type, two_type = csvtodict(char = char)

  allmat = np.zeros(shape=(len(charDict),matRowLen)); allcnt = 0
  zeromat = np.zeros(shape=(len(zero_type),matRowLen)) ; zerocnt = 0
  onemat = np.zeros(shape=(len(one_type),matRowLen)); onecnt = 0

  if char == 'class':
    twomat = np.zeros(shape=(len(two_type),matRowLen)); twocnt = 0
    max2LenArray = float('-inf')

  minbin = float('inf')
  maxbin = float('-inf')

  max0LenArray = float('-inf')
  max1LenArray = float('-inf')

  for arrfn in drctyArray:
    try:
      arr = np.load(arrfn)
      if not eig:
        arr = np.log(arr[arr.nonzero()])
      print "Processing %s..., length --> %d" % (arrfn, len(arr))
    except:
      print "[ERROR]: Line %s: Invariant file not found %s"  % (lineno(),arrfn)

    if eig:
      interp = (np.sort(arr)[::-1]) # reverse sort array

    else:
      pl.figure(1)
      n, bins, patches = pl.hist(arr, bins=numBins , range=None, normed=False, weights=None, cumulative=False, \
               bottom=None, histtype='stepfilled', align='mid', orientation='vertical', \
               rwidth=None, log=False, color=None, label=None, hold=None)

      n = np.append(n,0)
      n = n/float(sum(n))

      f = interpolate.interp1d(bins, n, kind='cubic')
      x = np.arange(bins[0],bins[-1],0.03) # vary linspc

      interp = f(x)
      ltz = interp < 0
      interp[ltz] = 0

      minbin  = bins[0] if bins[0] < minbin else minbin
      maxbin = bins[-1] if bins[-1] > maxbin else maxbin

      #min0bin  = bins[0] if bins[0] < min0bin else min0bin
      #max0bin = bins[-1] if bins[-1] > max0bin else max0bin

    if len(interp) > matRowLen:
      interp = interp[:(matRowLen-1)]
      print "File: %s, Truncated interpolation --> %d idx" % (arrfn,  matRowLen - (len(interp)))

    if len(interp) < matRowLen:
      #Pad array with zeros
      interp = np.append(interp, np.zeros(matRowLen - len(interp)))

    allmat[allcnt] = interp
    allcnt += 1

    # Populate each matrix by characterization
    if charDict[root(arrfn)] == '0':
      zeromat[zerocnt]  = interp
      zerocnt += 1
      max0LenArray = interp.nonzero()[0][-1] if interp.nonzero()[0][-1] > max0LenArray else max0LenArray

    elif charDict[root(arrfn)] == '1':
      onemat[onecnt] = interp
      onecnt += 1
      max1LenArray = interp.nonzero()[0][-1] if interp.nonzero()[0][-1] > max1LenArray else max1LenArray

    if char == 'class':
      if charDict[root(arrfn)] == '2':
        twomat[twocnt] = interp
        twocnt += 1
        max2LenArray = interp.nonzero()[0][-1] if interp.nonzero()[0][-1] > max2LenArray else max2LenArray

  if char == 'class':
    #return [allmat, zeromat, onemat, twomat]
    returnMats = [zeromat, onemat, twomat]

  if char == 'gender':
    returnMats = [zeromat, onemat]

  maxLenArrays = [max0LenArray, max1LenArray]

  for idx, mat in enumerate(returnMats):
    returnMats[idx] = trimMatrix(mat, maxLenArrays[idx])
  return [returnMats, [minbin,maxbin]]

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

def trimMatrix(mat, maxLenArray):
  #matdim1range = range(mat.shape[1])[::-1]
  #while 1:
  #  if np.array_equal(mat[:,-1], np.zeros_like(mat[:,-1])):
  #    mat = mat[:,:-1]
  #    print 'removing zeros'
  #  else:
  #    break
  return mat[:,:(maxLenArray-1)]

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



#########################################
#########################################

def pickprintcolor(charDict, arrfn):
  '''
  charDict: dict
  '''
  if (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '0'):
    plot_color = 'grey'
  elif (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '1'):
    plot_color = 'cyan'
  elif (charDict[(arrfn.split('/')[-1]).split('_')[0]] == '2'):
    plot_color = 'green'
  else:
    print "[ERROR]: %s, no match on subject type" % lineno()
  return plot_color

#########################################
#########################################
