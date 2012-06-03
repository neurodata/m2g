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
import itertools as itt
from matplotlib import pyplot as plt
    
def _load_fibergraph(roi_fn, mat_fn):
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
    ncc,vertexCC = sp.cs_graph_components(G+G.transpose())
        
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
        fg = _load_fibergraph(roiDir+brainFn+roiSfx,fiberDir+brainFn+fiberSfx)
                                   
        vcc = save_lcc(fg, ccDir+brainFn)
        
        if figDir:
            save_figures(get_cc_coords(vcc,10), figDir+brainFn)
        
        del fg
        
def get_cc_coords(vcc, ncc):
    """Computes coordinates for each voxel in the top ncc connected components"""
    inlcc = (np.less_equal(vcc,ncc)*np.greater(vcc,0)).nonzero()[0]
    coord = np.array([zindex.MortonXYZ(v) for v in inlcc])

    return np.concatenate((coord,vcc[inlcc][np.newaxis].T),axis=1)
    
def get_3d_cc(vcc,shape):
    """Takes an array vcc and shape which is the shape of the new 3d image and 'colors' the image by connected component
    
    Input
    =====
    vcc -- 1d array
    shape -- 3-tuple
    
    Output
    ======
    cc3d -- array of with shape=shape. colored so that ccz[x,y,z]=vcc[i] where x,y,z is the XYZ coordinates for Morton index i
    """

    cc3d = np.NaN*np.zeros(shape)
    allCoord = itt.product(*[xrange(sz) for sz in shape])
    
    [cc3d.itemset((xyz), vcc[zindex.XYZMorton(xyz)])
        for xyz in allCoord if not vcc[zindex.XYZMorton(xyz)]==0];
    return cc3d

def show_overlay(img3d, cc3d, ncc=10, s=85, xyz = 'xy'):
    """Shows the connected components overlayed over img3d
    
    Input
    ======
    img3d -- 3d array
    cc3d -- 3d array ( preferably of same shape as img3d, use get_3d_cc(...) )
    ncc -- where to cut off the color scale
    s -- slice to show
    xyz -- which projection to use in {'xy','xz','yz'}
    """
    if xyz=='xy':
        plt.imshow(img3d[:,:,s],cmap=plt.cm.gray_r)
        plt.imshow(cc3d[:,:,s],alpha=.7,cmap=plt.cm.jet,clim=(1,ncc))
    if xyz=='xz':
        plt.imshow(img3d[:,s,::-1].T,cmap=plt.cm.gray_r)
        plt.imshow(cc3d[:,s,::-1].T,alpha=.7,cmap=plt.cm.jet,clim=(1,ncc))
    if xyz=='yz':
        plt.imshow(img3d[s,::-1,::-1].T,cmap=plt.cm.gray_r)
        plt.imshow(cc3d[s,::-1,::-1].T,alpha=.7,cmap=plt.cm.jet,clim=(1,ncc))
    
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
    mlab.savefig(fn+'_view90,90.png',figure=vcf,magnification=4)
    mlab.close(f)
    
def check_fiber(fiber, fg,vcc):
    vox = list(fiber.getVoxels());
    
    x,y,z = zip(*[zindex.MortonXYZ(v) for v in vox])
    
    if np.min(x) >= 64 or np.max(x)<64:
        return 0
    
    if np.min(y) >= 65 or np.max(y)<55:
        return 0
    
    if np.min(z) >= 100 or np.max(z) < 90:
        return 0
    
    c = vcc[vox[0]]
    for v1 in vox:
        if fg.rois.get(zindex.MortonXYZ(v1))==0:
            continue
        
        
        for v2 in vox:
            if fg.rois.get(zindex.MortonXYZ(v2))==0 or v1 == v2:
                continue
            if fg.spcscmat[v1,v2]==0:
                return 1
        
        if vcc[vox]!=c:
            return 2
    return 0
            
            
            
    
    

    
if __name__=='__main__':
    fiberDir = '/mnt/braingraph1data/MRCAPgraphs/biggraphs/'
    roiDir = '/mnt/braingraph1data/MR.new/roi/'
    ccDir = '/data/biggraphs/connectedcomp/'
    figDir = '/home/dsussman/Dropbox/Figures/DTMRI/lccPics/'

    cc_for_each_brain(fiberDir, roiDir, ccDir, figDir)         