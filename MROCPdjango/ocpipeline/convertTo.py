import scipy.io as sio
import numpy as np
import os
import csv
from time import time

def convertLCCNpyToMat(lcc_fn):
  '''
  Convert a npy largest connected components file to an equivalent .mat file
  lcc_fn - largest connected components full file name which should be a .npy
  '''
  start  = time()
  lcc = np.load(lcc_fn).item().toarray()
  sio.savemat(os.path.splitext(lcc_fn)[0],{'lcc': lcc}, appendmat = True)
  print ('Lcc sucessfully converted from .npy to .mat in  %.2f secs') % (time()-start)


def convertArray(fn, toFormat, arrayName = "Array"):
  '''
  * Big graphs
  Covert an array between .npy, .csv, .mat
  fn - the filename of the file to be converted
  arrayName - the nickname of whatever is being converted e.g 'lcc' or 'triangles' or 'eigs'
  '''

  fnExt = os.path.splitext(fn)[1]
  fnBase = os.path.splitext(fn)[0]
  start  = time().item().toarray()
  if (fnExt == '.npy' and toFormat == '.mat'):
    arr = np.load(fn)
    sio.savemat(fnBase, {arrayName ,arr}, appendmat = True)

  elif (fnExt == '.mat' and toFormat == '.npy'):

    arr = sio.loadmat(fn) # Temp dict with headers etc + data
    dataMemberName = (set(arr.keys()) - set(['__version__', '__header__', '__globals__'])).pop()
    arr = arr[dataMemberName]
    np.save(fnBase, arr)

  elif ((fnExt == '.mat' or fnExt == '.npy') and toFormat == '.csv'):
    pass # TODO DM: Convert to csv

  else:
    print "[ERROR] in convertArray Invalid file format! Only .csv, .npy & .mat"
    sys.exit(-1)

  print ('%s sucessfully converted from .npy to .mat in  %.2f secs') % (arrayName, fnExt, toFormat ,(time()-start))


def convertGraph(G_fn, toFormat):
  '''
  Convert a graph from mat format to npy format
  G_fn - the graph name
  '''
  fnExt = os.path.splitext(fn)[1]

  if (fnExt == '.mat' and toFormat == '.npy'):
    start  = time()
    G = sio.loadmat(G_fn)['fibergraph']
    np.save(os.path.splitext(G_fn)[0],G)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif (fnExt == '.npy' and toFormat == '.mat'):
    start  = time()
    sio.savemat(os.path.splitext(G_fn)[0], {'fibergraph':np.load(G_fn)} , appendmat=True)
    print ('Graph successfully converted from .mat to .npy in  %.2f secs') % (time()-start)

  elif ((fnExt == '.npy' or fnExt == '.npy')  and toFormat == '.csv'):
    convertGraphToCSV(G_fn)

  else:
    print "[ERROR] in convertGraph Invalid file format! Only .csv, .npy & .mat"
    sys.exit(-1)

def convertSVDNpyToMat(svd_fn):
  '''
  Convert a npy sigular value decomposition file to an equivalent .mat file
  svd_fn - sigular value decomposition full file name which should be a .npy
  '''
  sio.savemat(os.path.splitext(svd_fn)[0],{'svd': np.load(svd_fn)}, appendmat = True)

def convertGraphToCSV(G_fn, G=None):
  '''
  * Infesible for big graphs ~9T space & 62 Days!
  Convert a graph .mat format to a dense comma separated value file (.csv)
  graph_fn - the full file name of the graph.
  '''
  fnExt = os.path.splitext(G_fn)[1]
  if not G:
    if (fnExt == '.mat'):
      G = sio.loadmat(G_fn)['fibergraph']
    if (fnExt == '.npy'):
      G = np.load(G_fn)

  if (G.shape[0] > 500):
    start = time()
    with open(os.path.splitext(G_fn)[0]+'.csv', 'wb') as csvfile:
      writer = csv.writer(csvfile, dialect='excel')
      for vertex in G.shape[0]:
        denseRow = np.array(G[vertex,:].todense())[0].tolist()
      writer.writerow(denseRow)
    print ('Graph successfully converted from %s to .csv in  %.2f secs') % (fnExt , (time()-start))

  else:
    print ('Sorry your graph is too big. Max size = 500 X 500')