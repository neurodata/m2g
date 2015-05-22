Basic Usage
***********


The overall workflow for the diffusion portion of M2G is shown in the image below.  
 
.. figure:: ../images/m2g_loni_overall.png
    :width: 800px
    :align: center
    
    LONI Overall Workflow

Inputs:

- List file specifying anatomical scans
- List file specifiying dti scans
- List file specifying dti parameters (bvalues and gradients)

Files within each list must be in correspondence to each other and must have the same length for proper pipelining operation.

The pipeline also requires the user to specify the atlas(es), reference structural volume and brain mask corresponding to the atlas(es). 

Outputs:  

- Graphs
- Other derivative products 

m2g is a 'one-click' pipeline, but the processing can be conceptually divided into two parts:  registration and diffusion processing.  

In the registration workflow, images are preprocessed (e.g, skull-stripped and denoised), and then registered.  Specifically, DTI volumes are registered to the B0 reference scan, the B0 scan is registered to the anatomical scan, and the anatomical scan is registered to the atlas (e.g., MNI) space.  Finally, these transforms are combined to create a DTI volume in atlas space so that scans and subjects can be easily compared.  

.. figure:: ../images/m2g_loni_registration.png
    :width: 800px
    :align: center
    
    LONI Registration Workflow

Finally, in the diffusion processing workflow, tensors are estimated for each voxel, indicating the primary direction of water diffusion at that location in the brain.  It has been shown that this corresponds to the principal direction of travel for major white matter (axonal) connections in the brain.  From the tensors, fiber streamlines, or tracks, are created using deterministic and probabilistic algorithms.  From the fibers and the atlas paracellations, we are able to estimate a graph.  

.. figure:: ../images/m2g_loni_diffusion.png
    :width: 800px
    :align: center
    
    LONI Diffusion Workflow

To generate a graph, we first form an empty graph (A), with rows and columns corresponding to nodes (atlas regions).  For each fiber streamline, we find all connected regions; for each pair of regions (i,j) in the streamline, we increment the A(i,j).  Because these connections are undirected, we also increment A(j,i) - or equivalently store only the upper triangular matrix. 

.. figure:: ../images/graph_construction.png
    :width: 800px
    :align: center
    
    Graph Construction Example

TODO:  Do we want more cartoon pictures or less? Not sure what the right balance is between LONI and cartoon.  We can do both!