#!/usr/bin/python

# convertTo.py
# Created by Disa Mhembere
# Email: dmhembe1@jhu.edu
# Copyright (c) 2013. All rights reserved.

"""
A module to load and convert graphs and invariant data between mat, npy and csv format
"""
import scipy.io as sio
import numpy as np
import os
import sys
import csv
from time import time
from django.conf import settings
import igraph
from csc_to_igraph import csc_to_igraph
from file_util import loadAnyMat

def convert_graph(gfn, informat, save_dir, *outformats):
  """
  Convert between igraph supported formats. No conversion to MAT or NPY available.

  @param gfn: the graph file name
  @param informat: the input format of the graph
  @param save_dir: the directory where we save result to
  @param outformat: a list of output formats
  """
  try:
    if informat in ["graphml", "ncol", "edgelist", "lgl", "pajek", "graphdb"]:
      g = igraph.read(gfn, None)
    elif informat == "mat":
      g = csc_to_igraph(loadAnyMat(gfn))
    elif informat == "npy":
      g = csc_to_igraph(np.load(gfn).item())
    else:
      err_msg = "[ERROR]: Unknown format '%s'. Please check format and re-try!" % informat
      print err_msg
      return err_msg
  except Exception, err_msg:
    print err_msg
    return "[ERROR]: "+str(err_msg)

  for fmt in outformats:
    fn = os.path.join(save_dir, os.path.splitext(os.path.basename(gfn))[0]+"."+fmt)
    print "Writing converted file %s ..." % fn
    g.write(fn, format=fmt)


def convertLCCNpyToMat(lcc_fn):
  '''
  Convert a npy largest connected components file to an equivalent .mat file.

  positional args:
  ================
  lcc_fn - largest connected components full file name which should be a .npy
  '''
  start  = time()
  lcc = np.load(lcc_fn).item().toarray()
  sio.savemat(os.path.splitext(lcc_fn)[0],{'lcc': lcc}, appendmat = True)
  print ('Lcc sucessfully converted from .npy to .mat in  %.2f secs') % (time()-start)

def convertSVDNpyToMat(svd_fn):
  '''
  Convert a npy sigular value decomposition file to an equivalent .mat file
  svd_fn - sigular value decomposition full file name which should be a .npy

  positional args:
  ================
  svd_fn - the full filename of the svd file
  '''
  sio.savemat(os.path.splitext(svd_fn)[0],{'svd': np.load(svd_fn)}, appendmat = True)


def convertAndSave(fn, toFormat, saveLoc, fileType):
  '''
  Convert invariant array between .npy, .csv, .mat.

  positional args:
  ================
  fn - the filename of the file to be converted
  toFormat - the desired output format i.e. a list with optional [.npy, .csv, .mat.].
  saveLoc - full path of where files are to be saved after conversion
  fileType - the fileType is the type of invariant ('cc','ss1', 'scanStat1')

  '''

  fnExt = os.path.splitext(fn)[1]
  fnBase = os.path.splitext(fn.split('/')[-1])[0] # eg. M854656235_degree

  if (fileType == "fg" or fileType == settings.VALID_FILE_TYPES[fileType]):
    for fmat in toFormat:
      convertGraph(fn, fmat, saveLoc)
    return

  start = time()
  arr = loadFile(fn, fileType) # load up the file as either a .mat, .npy

  if (('.mat' in toFormat) or 'mat' in toFormat):
    sio.savemat(os.path.join(saveLoc, fnBase), {fileType:arr}, appendmat = True)
    print fnBase + ' converted to mat format',

  if (('.npy' in toFormat) or ('npy' in toFormat)):
    np.save(os.path.join(saveLoc, fnBase), arr)
    print fnBase + ' converted to npy format',

  if (('.csv' in toFormat) or ('csv' in toFormat)):
    if (fileType == 'mad' or fileType == settings.VALID_FILE_TYPES[fileType]) : # Case of the MAD
      f = open(os.path.join(saveLoc, fnBase)+'.csv', 'wb')
      f.write(str(arr.item()))
      f.close

    else:
      try: # Means its eigenvector
        if (arr.shape[1] > 1):
          writeMultiRowCSV(arr, saveLoc, fnBase)
          print ('in %.2f secs') % ((time()-start))
          return
        else:
          pass
      except: # Means its eigenvalue so it can be written normally
        pass

      with open( os.path.join(saveLoc, fnBase)+'.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(arr)
      print fnBase + ' converted to csv format',

  print ('in %.2f secs') % ((time()-start))

def writeMultiRowCSV(data, saveLoc, fnBase):
  with open( os.path.join(saveLoc, fnBase)+'.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, dialect='excel')
    for row in range(data.shape[1]):
      writer.writerow(data[row])
  print fnBase + ' converted to csv format',



def convertGraph(G_fn, toFormat, saveLoc=None):
  '''
  Convert a graph from mat format to npy format

  positional args:
  ================
  G_fn - the graph name
  toFormat - the format to convert to. Either .mat, .npy, csv
  '''
  toFormat = '.'+toFormat if not toFormat.startswith('.') else toFormat
  fnExt = os.path.splitext(G_fn)[1]

  save_fn =  os.path.join(saveLoc, os.path.splitext(G_fn.split('/')[-1])[0] ) if saveLoc else os.path.splitext(G_fn)[0]

  if (fnExt == '.mat' and toFormat == '.npy'):
    start  = time()
    G = sio.loadmat(G_fn)['fibergraph']
    np.save(save_fn,G)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif (fnExt == '.npy' and toFormat == '.mat'):
    start  = time()
    sio.savemat(save_fn, {'fibergraph':np.load(G_fn)} , appendmat=True)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif ((fnExt == '.npy' or fnExt == '.mat')  and toFormat == '.csv'):
    convertGraphToCSV(G_fn, saveLoc=saveLoc)

  else:
    print "[ERROR] in convertGraph Invalid file format! Only .csv, .npy & .mat"
    sys.exit(-1)

def convertGraphToCSV(G_fn, G=None, saveLoc=None):
  '''
  Convert a graph .mat format to a dense comma separated value file (.csv)

  positional args:
  ================
  G_fn - the full file name of the graph file

  optional args:
  ================
  G - the actual graph loaded into memory already

  TODO:
  =====
  Infesible for big graphs ~9T space & 62 Days!
  '''
  fnExt = os.path.splitext(G_fn)[1]
  if not G:
    if (fnExt == '.mat'):
      G = sio.loadmat(G_fn)['fibergraph']
    if (fnExt == '.npy'):
      G = np.load(G_fn)

  save_fn =  os.path.join(saveLoc, os.path.splitext(G_fn.split('/')[-1])[0] ) if saveLoc else os.path.splitext(G_fn)[0]

  if (G.shape[0] < 1000):
    start = time()
    with open(save_fn+'.csv', 'wb') as csvfile:
      writer = csv.writer(csvfile, dialect='excel')
      for vertex in range(G.shape[0]):
        denseRow = np.array(G[vertex,:].todense())[0].tolist()
        writer.writerow(denseRow)
    print ('Graph successfully converted from %s to .csv in  %.2f secs') % (fnExt , (time()-start))

  else:
    print ('Sorry your graph is too big. Max size = 500 X 500')

def loadFile(file_fn, fileType):
  '''
  Determine how to load a file based on the extension &
  the fileType

  positional args:
  ================
  file_fn  - the filename of the file to be loaded.
  fileType - the fileType to loaded.

  returns:
  =======
  the loaded file

  The following are valid fileTypes:
      1. 'cc'|'clustCoeff' is the clustering coefficient
      2. 'deg'|'degree' is the local vertex degree
      3. 'eig'|'eigen' is the eigenvalues
      4. 'mad'|'maxAvgDeg'
      5. 'ss1'| 'scanStat1'
      6. 'ss2'| 'scanStat2'
      7. 'tri'|'triangle'
      8. 'svd'|'singValDecomp'
  '''

  fn, ext = os.path.splitext(file_fn)
  if (ext == '.mat' and  fileType in settings.VALID_FILE_TYPES.keys()):
      theFile = sio.loadmat(file_fn)[fileType]

  elif (ext == '.mat'and fileType in settings.VALID_FILE_TYPES.values()):  # All currently available
    theFile = sio.loadmat(file_fn)[settings.VALID_FILE_TYPES[fileType]]
    #arr = sio.loadmat(fn) # Temp dict with headers etc + data
    #dataMemberName = (set(arr.keys()) - set(['__version__', '__header__', '__globals__'])).pop() # extract data member from .mat
    #arr = arr[dataMemberName]

  elif (ext == '.npy'):
    if (fileType == "lcc" or fileType == settings.VALID_FILE_TYPES[fileType]):
      theFile = np.load(file_fn).item().toarray()[0] # unsparsify
    else:
      theFile = np.load(file_fn)

  elif (ext == '.csv'): # CSV for invariants only graphs will not work
    f = open(file_fn,'rt')
    try:
      reader = csv.reader(f)
      theFile = reader.next() # Expecting one line with all invariant values
    except:
      print "[ERROR:] CSV read file failure!"
    finally:
      f.close()
    theFile = np.array(theFile)

  return theFile
