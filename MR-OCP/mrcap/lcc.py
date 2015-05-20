
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

'''
Created on Mar 12, 2012

@author: dsussman
'''
import pyximport;
pyximport.install()

import numpy as np
from scipy import sparse as sp
import mrcap.roi as roi
import mrcap.fibergraph as fibergraph
import zindex
from scipy.io import loadmat, savemat
from collections import Counter
#from mayavi import mlab # DM - commented out
import itertools as itt
# from matplotlib import pyplot as plt # DM - commented out
import mrcap.fa as fa
#import mprage # DM - commented out
import argparse
import os

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

    def save(self,fn, suffix=True):
        if suffix:
            np.save(fn+'_concomp.npy',sp.lil_matrix(self.vertexCC))
        else:
            np.save(fn,sp.lil_matrix(self.vertexCC))

    def load_from_file(self,fn):
        self.vertexCC = np.load(fn).item().toarray()
        self.n = self.vertexCC.shape[1]
        self.vertexCC = self.vertexCC.reshape(self.n)

    def induced_subgraph(self, G, cc=1):
        incc = np.equal(self.vertexCC,cc).nonzero()[0]
        return G[:,incc][incc,:]


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
        vcc = ConnectedComponent(fg.graph)
        vcc.save(ccDir+brainFn)

        print 'ncc='+repr(vcc.ncc)


        if figDir:
            save_figures(vcc.get_coords_for_lccs(10), figDir+brainFn)

        del fg

'''
Created on June 29, 2012
@author: dmhembe1

Determine lcc on a single big graph a provided my a remote user
This is for use in the one-click processing pipeline to be found at http://www.openconnecto.me/STUB
'''
def process_single_brain(graph_fn, lccOutputFileName):
    print "Computint LCC for single brain... "
    vcc = ConnectedComponent(loadmat(graph_fn)['fibergraph'])
    if not os.path.exists(os.path.dirname(lccOutputFileName)):
      print "Creating lcc directory %s" % os.path.dirname(lccOutputFileName)
      os.makedirs(os.path.dirname(lccOutputFileName))

    lcc = sp.lil_matrix(vcc.vertexCC)
    np.save(lccOutputFileName, lcc) # save as .npy
    return lcc


def get_slice(img3d, s, xyz):
    if xyz=='xy':
        return img3d[:,:,s]
    if xyz=='xz':
        return img3d[:,s,::-1].T
    if xyz=='yz':
        return img3d[s,::-1,::-1].T

    print 'Not a valid view'

def show_overlay(img3d, cc3d, ncc=10, s=85, xyz = 'xy',alpha=.8):
    """Shows the connected components overlayed over img3d

    Input
    ======
    img3d -- 3d array
    cc3d -- 3d array ( preferably of same shape as img3d, use get_3d_cc(...) )
    ncc -- where to cut off the color scale
    s -- slice to show
    xyz -- which projection to use in {'xy','xz','yz'}
    """
    cc = get_slice(cc3d,s,xyz)
    img = get_slice(img3d,s,xyz)

    notcc = np.isnan(cc)
    incc = np.not_equal(notcc,True)

    img4 = plt.cm.gray(img/np.nanmax(img))
    if ncc is not np.Inf:
        cc = plt.cm.jet(cc/float(ncc))
    else:
        cc = plt.cm.jet(np.log(cc)/np.log(np.nanmax(cc)))

    cc[notcc,:]=img4[notcc,:]
    cc[incc,3] = 1-img[incc]/(2*np.nanmax(img))

    plt.imshow(cc)

    #if ncc is not np.Inf:
    #    plt.imshow(cc,cmap=plt.cm.jet,clim=(1,ncc))
    #else:
    #    plt.imshow(np.log(cc),cmap=plt.cm.jet)
    #plt.imshow(img,alpha=alpha,cmap=plt.cm.gray)

def save_fa_overlay(faDir, ccDir, figDir, slist, orientationList):
    brainFiles = [fn.split('_')[0] for fn in os.listdir(ccDir)]
    f = plt.figure();

    for bfn in brainFiles:
        vcc = ConnectedComponent(fn=ccDir+bfn+'_concomp.npy')
        fax = fa.FAXML(faDir+bfn+'_fa.xml')
        fas = fa.FAData(faDir+bfn+'_fa.raw',fax.getShape())
        cc3d = vcc.get_3d_cc(fax.getShape())

        for view,s,xyz in zip(np.arange(len(slist)),slist,orientationList):
            show_overlay(fas.data,cc3d,np.Inf,s,xyz,.5)
            plt.savefig(figDir+bfn+'_ccfaOverlay_view'+repr(view)+'.pdf',)
            plt.clf()

    plt.close(f)



def save_overlay(faDir, mprDir, ccDir, figDir, slist, orientationList):
    brainFiles = [fn.split('_')[0] for fn in os.listdir(ccDir)]
    f = plt.figure(figsize=(14,9));

    for bfn in brainFiles:
        vcc = ConnectedComponent(fn=ccDir+bfn+'_concomp.npy')
        fax = fa.FAXML(faDir+bfn+'_fa.xml')
        fas = fa.FAData(faDir+bfn+'_fa.raw',fax.getShape())
        mpx = mprage.MPRAGEXML(mprDir+'mprage_'+bfn+'_ss_crop.xml')
        mpd = mprage.MPRAGEData(mprDir+'mprage_'+bfn+'_ss_crop.raw',mpx.getShape())

        cc3d = vcc.get_3d_cc(fax.getShape())

        for view,s,xyz in zip(np.arange(len(slist)),slist,orientationList):

            plt.clf()
            plt.subplot(221);
            plt.title('FA Overlay')
            show_overlay(fas.data,cc3d,np.Inf,s,xyz,.5)

            plt.subplot(222);
            plt.title('FA Original; '+bfn+', '+xyz+'-slice '+repr(s))
            plt.imshow(get_slice(fas.data,s,xyz),cmap=plt.cm.gray)
            plt.colorbar()

            plt.subplot(223); plt.title('MPRAGE Overlay')
            show_overlay(mpd.data,cc3d,np.Inf,s,xyz,.5)

            plt.subplot(224);
            plt.title('MPRAGE Original')
            plt.imshow(get_slice(mpd.data,s,xyz),cmap=plt.cm.gray)
            plt.colorbar()

            #plt.tight_layout()
            plt.savefig(figDir+bfn+'_ccfaOverlay_view'+repr(view)+'.pdf')

    plt.close(f)

'''
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
'''

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

def main ():

    parser = argparse.ArgumentParser(description='Draw the ROI map of a brain.')
    parser.add_argument('roixmlfile', action="store")
    parser.add_argument('roirawfile', action="store")
    parser.add_argument('fibergraphfile', action="store")
    parser.add_argument('ccfile', action="store")

    result = parser.parse_args()

    roix = roi.ROIXML(result.roixmlfile)
    rois = roi.ROIData(result.roirawfile, roix.getShape())

    fg = fibergraph.FiberGraph(roix.getShape(),rois,[])
    fg.loadFromMatlab('fibergraph', result.fibergraphfile)

    vcc = ConnectedComponent(G=fg.graph)
    vcc.save(results.ccfile)


if __name__=='__main__':

    # Added for -h flag # DM
    parser = argparse.ArgumentParser(description="Largest connected component generator")
    result =  parser.parse_args()

    graphDir = '/mnt/braingraph1data/projects/MRN/graphs/biggraphs/'
    roiDir = '/mnt/braingraph1data/projects/will/mar12data/roi/'
    ccDir = '/data/biggraphs/connectedcomp/'
    figDir = '/home/dsussman/Dropbox/Figures/DTMRI/lccPics/'

    cc_for_each_brain(graphDir, roiDir, ccDir, figDir)
