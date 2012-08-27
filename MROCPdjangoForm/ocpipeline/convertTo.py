import scipy.io as sio
import numpy as np
import os
import csv

def convertLCCtoMat(lcc_fn):
  '''
  Convert a npy largest connected components file to an equivalent .mat file
  lcc_fn - largest connected components full file name which should be a .npy
  '''
  lcc = np.load(lcc_fn).item().toarray()
  sio.savemat(os.path.splitext(lcc_fn)[0],{'lcc': lcc}, appendmat = True)
  print ('Lcc sucessfully saved as mat')
  
def convertSVDtoMat(svd_fn):
  '''
  Convert a npy sigular value decomposition file to an equivalent .mat file
  svd_fn - sigular value decomposition full file name which should be a .npy
  '''
  sio.savemat(os.path.splitext(svd_fn)[0],{'svd': np.load(svd_fn)}, appendmat = True)
  
def convertGraphToCSV(graph_fn):
  '''
  Convert a graph .mat format to one comma separated value file (.csv)
  graph_fn - the full file name of the graph. 
  '''
  gr_csc = sio.loadmat(graph_fn)['fibergraph'] # key is always fibergraph
  dense_gr_csc = graph_csc.todense()
  gr_list = dense_g_csc.tolist()
  
  ##### ***** MORE HERE ****** ######
    
  gr_csv = csv.writer(gr_list, dialect='excel', )
  
  
  