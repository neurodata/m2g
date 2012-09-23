'''
Created on Feb 19, 2012

@author: dsussman
Copyright (c) 2012 Johns Hopkins University. All rights reserved.
'''

import numpy as np
# import networkx as nx # Disa - Not necessary for OCP
import scipy.sparse as sparse
from scipy.sparse import linalg as la
from scipy import linalg
#from sklearn.cluster import KMeans # Disa - Not necessary for OCP
from itertools import product

def adjacency_matrix(G):
    """Returns the adjacency matrix of a networkx graph as an np.array"""
    return np.array(nx.adjacency_matrix(G))

def marchette_matrix(G):
    A = np.array(nx.adjacency_matrix(G))
    dia = A.dot(np.ones(A.shape[0]))/(G.number_of_nodes()-1)
    return A + np.diag(dia)

# adjacency_sparse = nx.to_scipy_sparse_matrix # Disa - Edit

def laplacian_sparse(G):
    """Returns a scipy.sparse version of the normalized laplacian as given in Rohe, et al.
    
    L  = D^{-1/2}AD^{-1/2} where D is the diagonal matrix of degree"""
    n = G.number_of_nodes()
    A = nx.to_scipy_sparse_matrix(G)
    degree =  A*np.ones(n)
    scale = sparse.lil_matrix((n,n))
    scale.setdiag([np.sqrt(1.0/deg) if deg!=0 else 0 for deg in degree])
    #scale = np.array([np.sqrt(d**-1) if d!=0 else 0 for d in degree])
    return scale*A*scale

def laplacian_matrix(G):
    """Returns an np.array version of the normalized laplacian as given in Rohe, et al.
    
    L  = D^{-1/2}AD^{-1/2} where D is the diagonal matrix of degree"""
    n = G.number_of_nodes()
    A = np.array(nx.adjacency_matrix(G))
    degree = np.dot(A,np.ones(n))
    scale = [np.sqrt(1.0/deg) if deg!=0 else 0 for deg in degree]
    return np.dot(np.diag(scale),np.dot(A, np.diag(scale)))

def self_matrix(G):
    """A function for embedding if G is already stored in matrix form"""
    return G

class Embed(object):
    """Class do perform spectral embedding of Graphs"""
    dim = None
    
    sval = None
    svec = None
    svecR = None
    
    matrix = None
    G = None
    directed = False
    
    def __init__(self, dim, matrix=adjacency_matrix, directed=False):
        """Initializes an Embed object
        
        Inputs
        =======
        dim -- dimension of the embeding
        matrix -- function which returns a matrix which represents the graph
                  the default is the (dense) adjacency matrix as an np.array
                  The matrix must return something that is accepted by 
                  scipy.sparse.linalg.svds
        """
        self.dim = dim
        self.matrix = matrix
        self.directed = directed
    
    
    def __check_dim(self,d):
        """Helper function to make sure this is a valid dimension to return"""
        if d<1:
            raise ValueError('Dimension must be >=1')
        if d>self.dim:
            raise ValueError('Dimension must be <=self.dim')
        
    def embed(self, G, fast=True):
        """Calculate the matrix for the graph and embed it to self.dim dimnensions
        
        Uses the dim largest singular values.
        
        Inputs
        ======
        G - the graph object, must be acceptable as a parameter for self.matrix
        fast -- if true then don't check if self.G==G before re-doing the embedding
        """ 
        if not fast or self.G is not G:
            self.G = G
            if not self.directed:
                self.svec,self.sval,_ = la.svds(self.matrix(G), self.dim)
            else:
                self.svec,self.sval,self.svecR = la.svds(self.matrix(G), self.dim)
                self.svecR = self.svecR[:, ::-1].T
            self.sval = self.sval[::-1]
            self.svec = self.svec[:, ::-1]
            
        return self
        
    def get_embedding(self, d=None, scale=None):
        """Return the scaled or unscaled version of the embedding
        
        Inputs
        ======
        d -- dimension you want for the embedding, None for self.dim
        scale -- whether the singular vectors should be scaled by the square root singular values
        """
        if scale:
            return self.get_scaled(d)
        else:
            return self.get_unscaled(d)
    
    def get_unscaled(self, d=None):
        """Return the unscaled version of the embedding
        
        Inputs
        ======
        d -- dimension you want for the embedding, None for self.dim
        """
        if not d:
            d=self.dim
        
        self.__check_dim(d)
        
        if not self.directed:
            return self.svec[:,np.arange(d)]
        else:
            return np.concatenate((self.svec[:,np.arange(d)], self.svecR[:,np.arange(d)]),1)
        
    def get_scaled(self, d=None):
        """Return the scaled version of the embedding
        
        Inputs
        ======
        d -- dimension you want for the embedding, None for self.dim
        """
        if not d:
            d=self.dim
        self.__check_dim(d)
        
        if not self.directed:
            return np.dot(self.svec[:,np.arange(d)], 
                        np.diag(np.sqrt(self.sval[np.arange(d)])))
        else:
            return np.concatenate((
                np.dot(self.svec[:,np.arange(d)], 
                        np.diag(np.sqrt(self.sval[np.arange(d)]))),
                np.dot(self.svecR[:,np.arange(d)], 
                        np.diag(np.sqrt(self.sval[np.arange(d)]))) ),1)
            
    def get_P_matrix(self, d=None):
        x = self.get_scaled(d)
        if not self.directed:
            P = x.dot(x.T)
        else:
            P = x[:,:d].dot(x[:,d:].T)
            
        eps = .0001
        P[P<0]= eps
        P[P>1]=1-eps
            
        return P-np.diag(np.diag(P))
        
class EmbedIter(object):
    """Object to iterate over different matrices, dimensions, scale/unscaled embeddings"""
    d = []
    matrix = []
    embed = None
    
    def __init__(self, d_range, matrices, scales):
        """Initiate with lists of dimensions, matrices, scales"""
        self.d = d_range
        self.matrix = matrices
        self.scale = scales
        self.embed = [Embed(np.max(self.d), m) for m in self.matrix]
        
        
    def get_embedding(self, G):
        for ( d,embed, scale) in product(self.d, self.embed, self.scale):
            embed.embed(G)
            yield embed.get_embedding(d, scale)
        
        
    
adjEmbed = Embed(10,matrix=adjacency_matrix)
lapEmbed = Embed(10,matrix=laplacian_matrix)
marEmbed = Embed(10,matrix=marchette_matrix)
    

def dot_product_embed(G, d, scaled=True):
    """ Generates an n by d matrix using an svd of the adjacency matrix
    
    Each row of the output corresponds to a node (ordered according to G.node)
    so that each node is assigned a vector in d-dimensional euclidean space.
    
    Parameters
    ----------
    G -- networkx graph
    d -- embedding dimension
    scaled -- whether to scaled the embedding by the square root
             of the eigenvalues (default=True) 
             
    Returns
    -------
    n times d matrix where n=G.number_of_nodes()
    """
    A = adjacency_matrix(G)
    if scaled:
        u,s,_ = la.svds(A, d)
        return np.dot(u,np.diag(np.sqrt(s)))
    else:
        u,_,_ = la.svds(A, d)
        return u

dot_product_embed_unscaled = lambda G,d: dot_product_embed(G,d,scaled=False)

def normalized_laplacian_embed(G,d, scaled=False):
    """ Generates an n by d matrix using an svd of the normalized laplacian
    
    Each row of the output corresponds to a node (ordered according to G.node)
    so that each node is assigned a vector in d-dimensional euclidean space.
    
    Parameters
    ----------
    G -- networkx graph
    d -- embedding dimension
    scaled -- whether to scaled the embedding by the square root
             of the eigenvalues (default=False) 
             
    Returns
    -------
    n times d matrix where n=G.number_of_nodes()
    """
    L  = laplacian_matrix(G)
    
    if scaled:
        u,s,_ = la.svds(sparse.csr_matrix(L), d)
        return np.dot(u,np.diag(np.sqrt(s)))
    else:
        u,_,_ = la.svds(sparse.csr_matrix(L), d)
        return u
        
normalized_laplacian_embed_scaled = lambda G,d:normalized_laplacian_embed(G, d, scaled=True)
        
def cluster_vertices_kmeans(G, embed, d, k, name=None):
    """ Clusters vertices into k groups based on an embedding in d dimensions
    
    Parameters
    ----------
    G -- networkx graph
    embed -- embedding method takes 2 paramets, Graph and dimension
    d --  embedding dimension
    k -- number of clusters
    name -- if not None then assign labels as attribute name to each node
    """
    k_means = KMeans(init='k-means++', k=k, n_init=10)
    x = embed(G, d)
    k_means.fit(x)
    label = k_means.labels_
    if name is not None:
        nx.set_node_attributes(G, name, dict(zip(np.arange(G.number_of_nodes()),label)))

    return label



def procrustes(X,Y):
    """Finds the optimal affine transformation T to minimize ||x-Ty||_F
    
    Parameters
    ----------
    x - reference, shape(x)=nxd where n is number of samples and d is dimension
    y - to be aligned, shape(x)=nxd
    
    Returns
    -------
    Z - the transformed y
    
    TODO: return T -  the transformation
    TODO: make scaling, reflection, centering optional
    TODO: allow different dimension
    """
    
    assert(X.shape == Y.shape)
    
    # Center
    muX = np.mean(X,axis=0)
    muY = np.mean(Y,axis=0)
    X0 = X-muX
    Y0 = Y-muY
    
    # Scale
    varX = np.var(X0,axis=0)
    varY = np.var(Y0,axis=0)
    
    #Rotate
    l,d,m = linalg.svd(X0.T.dot(Y0))
    Z = np.sqrt(np.sum(varX)/np.sum(varY))*Y0.dot(m).dot(l.T)+muX
    
    return Z