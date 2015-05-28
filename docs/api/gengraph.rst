Graph Generation
****************

.. autofunction:: mrcap.gengraph.genGraph


Intuition Behind Graph Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To generate a graph, we first form an empty graph (A), with rows and columns corresponding to nodes (atlas regions).  For each fiber streamline, we find all connected regions; for each pair of regions (i,j) in the streamline, we increment the A(i,j).  Because these connections are undirected, we also increment A(j,i) - or equivalently store only the upper triangular matrix. 

.. figure:: ../images/graph_construction.png
    :width: 800px
    :align: center

Pseudocode
~~~~~~~~~~
