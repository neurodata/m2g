Introduction
************

The ability to estimate a connectome, i.e. a description of connectivity in the brain, promises advances in many areas from personalized medicine to learning and education, and even to intelligence analysis. Advances in imaging have allowed researchers to create datasets containing hundreds to thousands of brain images; m2g offers a robust solution to estimate brain graphs at scale.

Our pipline creates reproducible graphs that give the community the ability to ‘’classify’’ an individual’s connectome. Traits such as gender, handedness, intelligence, the ability to learn a foreign language, psychological impairments, disease susceptibility, etc., are all things which can be studied through the lens of brain graphs.

The primary contribution of our efforts is the creation of a robust, high-throughput pipeline for estimating connectomes, beginning with diffusion MR images and MPRAGE structural data and ending with both small (70 vertex) , and big (1 million vertex) brain graphs.


.. image:: ../images/m2g.png

m2g estimates brain graphs from multimodal MRI through a series of steps which are illustrated above. Before advanced processing can occur, the images must first be aligned into the same physical space as one another, as well as a template atlas which contains labeling information of the regions. Then, tensors are estimated from the diffusion data and fibers traced using the deterministic FACT algorithm. Once fiber streamlines are obtained, the graphs are generated through a look-up process which maps voxels along the fibers to regions within the atlas. The generated graphs are then analyzed and reliability of the pipeline assessed, using a dataset with test-retest scans.
