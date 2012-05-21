'''
Created on Mar 12, 2012

@author: dsussman
'''
import pyximport;
pyximport.install()

import os
import numpy as np
from scipy import sparse as sp 
import roi
import fibergraph
import zindex
from scipy.io import loadmat, savemat
from collections import Counter
from mayavi import mlab
    
def load_fibergraph(roi_fn, mat_fn):
    """Load fibergraph from roi_fn and mat_fn"""
    
    roix = roi.ROIXML(roi_fn+'.xml')
    rois = roi.ROIData(roi_fn+'.raw', roix.getShape())
    
    fg = fibergraph.FiberGraph(roix.getShape(),rois,[])
    fg.loadFromMatlab('fibergraph', mat_fn)
    
    return fg
    
    
    
def get_lcc_idx(G):
    """Determines and sorts the connected components of G
    
    Each vertex in G is assigned a label corresponding to its connected component.
    The largest connected component is labelled 0, second largest 1, etc.
    
    **NOTE**: All isolated vertices (ie no incident edges) are put in 1 connected components
    """
    ncc,vertexCC = sp.cs_graph_components(G)
        
    cc_size = Counter(vertexCC)
    cc_size = sorted(cc_size.iteritems(), key=lambda cc: cc[1],reverse=True)
    cc_badLabel,_ = zip(*cc_size)
    cc_dict = dict(zip(cc_badLabel, np.arange(ncc+1)))
    
    vertexCC = [cc_dict[vcc] for vcc in vertexCC]
   
    return np.array(vertexCC)
    
def save_lcc(fg, fn):
    """Save the largest connected component for this fibergraph in file fn"""
    vcc = get_lcc_idx(fg.spcscmat)
    np.save(open(fn+'_concomp.npy','w'),vcc)
    savemat(fn+'_concomp.mat',{'vertexCC':vcc})
    return vcc
    
def cc_for_each_brain(fiberDir, roiDir, ccDir, figDir):
    """Go through the directory fiberDir and find the connected components
    
    Saves the all connected component info in ccDir and saves some 3d-pics into figDir
    If figDir is None then it does not save
    """

    fiberSfx = '_fiber.mat'
    roiSfx = '_roi'
    
    brainFiles = [fn.split('_')[0] for fn in os.listdir(fiberDir)]
    
    for brainFn in brainFiles:
        print "Processing brain "+brainFn
        fg = load_fibergraph(roiDir+brainFn+roiSfx,fiberDir+brainFn+fiberSfx)
                                   
        vcc = save_lcc(fg, ccDir+brainFn)
        
        if figDir:
            save_figures(get_cc_coords(vcc,10), figDir+brainFn)
        
        del fg
        
def get_cc_coords(vcc, ncc):
    """Computes coordinates for each voxel in the top ncc connected components"""
    inlcc = (np.less_equal(vcc,ncc)*np.greater(vcc,0)).nonzero()[0]
    coord = np.array([zindex.MortonXYZ(v) for v in inlcc])

    return np.concatenate((coord,vcc[inlcc][np.newaxis].T),axis=1)
    
def cc_to_coord(vcc,shape):
    """Takes an array vcc and shape which is the shape of the new 3d image and 'colors' the image by connected component
    
    Input
    =====
    vcc -- 1d array
    shape -- 3-tuple
    
    Output
    ======
    ccz -- array of with shape=shape. colored so that ccz[x,y,z]=vcc[i] where x,y,z is the XYZ coordinates for Morton index i
    """
    ccz = np.zeros(shape)
    [ccz.itemset(tuple(zindex.MortonXYZ(i)), vcc[i]) for i in xrange(len(vcc))]
    return ccz
    
def save_figures(coord, fn):
    """Saves 3 images which are 3d color representations of the coordinates in coord
    
    Input
    =====
    coord -- an nx4 array of x,y,z coordinates and another scalar that gives color
    fn -- save filename prefix"""
    x,y,z,c = np.hsplit(coord,4)
    
    f = mlab.figure()
    mlab.points3d(x,y,z,c, mask_points=50, scale_mode='none',scale_factor=2.0)
    mlab.view(0,180)
    mlab.savefig(fn+'_view0,180.png',figure=f,magnification=4)
    mlab.view(0,90)
    mlab.savefig(fn+'_view0,90.png',figure=f,magnification=4)
    mlab.view(90,90)
    mlab.savefig(fn+'_view90,90.png',figure=f,magnification=4)
    mlab.close(f)
    
    
if __name__=='__main__':
    fiberDir = '/mnt/braingraph1data/MRCAPgraphs/biggraphs/'
    roiDir = '/mnt/braingraph1data/MR.new/roi/'
    ccDir = '/data/biggraphs/connectedcomp/'
    figDir = '/home/dsussman/Dropbox/Figures/DTMRI/lccPics/'

    cc_for_each_brain(fiberDir, roiDir, ccDir, figDir)         