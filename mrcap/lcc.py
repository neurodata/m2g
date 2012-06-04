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

class ConnectedComponent(object):
    vertexCC = None
    ccsize = None
    ncc = 0
    n = 0
    
    def __init__(self,G=None, fn=None):
        if G is not None:
            self.get_from_fiber_graph(G)
        elif fn is not None:
            self.load_from_file(fn)
            
    def get_from_fiber_graph(self,G):
        self.ncc,vertexCC = sp.cs_graph_components(G+G.transpose())
        
        self.n = vertexCC.shape[0]
        
        noniso = np.nonzero(np.not_equal(vertexCC,-2))[0]
        
        cccounter = Counter(vertexCC[noniso])
        cc_badLabel,_ = zip(*cccounter.most_common())
        cc_dict = dict(zip(cc_badLabel, np.arange(self.ncc)+1))
        cc_dict[-2] = 0
        
        self.vertexCC = np.array([cc_dict[v] for v in vertexCC])
        self.ccsize = Counter(vertexCC)
    
    def save(self,fn):
        np.save(fn+'_concomp.npy',sp.lil_matrix(self.vertexCC))
        
    def load_from_file(self,fn):
        self.vertexCC = np.load(fn).item().toarray()
        self.n = self.vertexCC.shape[1]
        self.vertexCC = self.vertexCC.reshape(self.n)

    
    def __getitem__(self,key):
        if type(key) is int:
            return self.get_cc(key)
        elif type(key) is tuple:
            return self.get_coord_cc(key)
        
    def get_cc(self,v):
        return self.vertexCC[v]
        
    def get_coord_cc(self,xyz):
        return self.get_cc(zindex.XYZMorton(xyz))
        
    def get_3d_cc(self,shape):
        """Takes a shape which is the shape of the new 3d image and 'colors' the image by connected component
        
        Input
        =====
        shape -- 3-tuple
        
        Output
        ======
        cc3d -- array of with shape=shape. colored so that ccz[x,y,z]=vcc[i] where x,y,z is the XYZ coordinates for Morton index i
        """
    
        cc3d = np.NaN*np.zeros(shape)
        allCoord = itt.product(*[xrange(sz) for sz in shape])
        
        [cc3d.itemset((xyz), self.vertexCC[zindex.XYZMorton(xyz)])
            for xyz in allCoord if not self.vertexCC[zindex.XYZMorton(xyz)]==0];
        return cc3d
    
    def get_coords_for_lccs(self, ncc):
        """Computes coordinates for each voxel in the top ncc connected components"""
        inlcc = (np.less_equal(self.vertexCC,ncc)*np.greater(self.vertexCC,0)).nonzero()[0]
        coord = np.array([zindex.MortonXYZ(v) for v in inlcc])
    
        return np.concatenate((coord,self.vertexCC[inlcc][np.newaxis].T),axis=1)
    
def _load_fibergraph(roi_fn, mat_fn):
    """Load fibergraph from roi_fn and mat_fn"""
    
    roix = roi.ROIXML(roi_fn+'.xml')
    rois = roi.ROIData(roi_fn+'.raw', roix.getShape())
    
    fg = fibergraph.FiberGraph(roix.getShape(),rois,[])
    fg.loadFromMatlab('fibergraph', mat_fn)
    
    return fg
    

def cc_for_each_brain(graphDir, roiDir, ccDir, figDir):
    """Go through the directory graphDir and find the connected components
    
    Saves the all connected component info in ccDir and saves some 3d-pics into figDir
    If figDir is None then it does not save
    """

    fiberSfx = '_fiber.mat'
    roiSfx = '_roi'
    
    brainFiles = [fn.split('_')[0] for fn in os.listdir(graphDir)]
    
    for brainFn in brainFiles:
        print "Processing brain "+brainFn
        fg = _load_fibergraph(roiDir+brainFn+roiSfx,graphDir+brainFn+fiberSfx)
                        
                        
        print 'Processing connected components'
        vcc = ConnectedComponent(fg.spcscmat)
        vcc.save(ccDir+brainFn)
        
        print 'ncc='+repr(vcc.ncc)
        
        if figDir:
            save_figures(vcc.get_coords_for_lccs(10), figDir+brainFn)
        
        del fg
    

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
    mlab.savefig(fn+'_view90,90.png',figure=f,magnification=4)
    mlab.close(f)

def get_3d_cc(vcc,shape):
    """Takes an array vcc and shape which is the shape of the new 3d image and 'colors' the image by connected component
    
    For some reason this is 3 times as fast as the same thing in the ConnectedComponet class ?
    
    Input
    =====
    vcc  1d array
    shape  3tuple
    
    Output
    ======
    cc3d  array of with shape=shape. colored so that ccz[x,y,z]=vcc[i] where x,y,z is the XYZ coordinates for Morton index i
    """

    cc3d = np.NaN*np.zeros(shape)
    allCoord = itt.product(*[xrange(sz) for sz in shape])
    
    [cc3d.itemset((xyz), vcc[zindex.XYZMorton(xyz)])
        for xyz in allCoord if not vcc[zindex.XYZMorton(xyz)]==0];
    return cc3d
    

    
if __name__=='__main__':
    graphDir = '/mnt/braingraph1data/projects/MRN/graphs/biggraphs/'
    roiDir = '/mnt/braingraph1data/projects/will/mar12data/roi/'
    ccDir = '/data/biggraphs/connectedcomp/'
    figDir = '/home/dsussman/Dropbox/Figures/DTMRI/lccPics/'

    cc_for_each_brain(graphDir, roiDir, ccDir, figDir)         