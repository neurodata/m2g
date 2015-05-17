.. M2G is kinda good.
.. meta::
   :description: Official documentation for M2G:  MR Images to Graphs 
   :keywords: MRI, pipeline, neuroscience, diffusion, resting state
.. title::
   m2g

.. raw:: html

	<h1>m2g:  Framework for robust, reliable MR connectome estimation</h1>
	<br>

.. image:: images/m2g.png


.. raw:: html
  
  <hr>
  <p>This page describes how brain graphs are generated in our service from Diffusion Weighted MRI (dMRI), and structural MRI (sMRI) images of human brains. The MRImages to Graphs (M2G) pipeline is the successor of MRCAP and MIGRAINE. M2G combines dMRI and sMRI data from a single subject to estimate a high-level connectome. The connectomes returned describe regions of connectivity within the brain at multiple levels of resolution - from a single voxel scale ~1 mm<sup>3</sup> to large cortical regions ~20 cm<sup>3</sup>.</p>

  <p> M2G has been developed in the LONI pipelining environment. This environment enforces that the pipeline be modular in construction, and all created workflows and modules are command-line executable. This makes M2G efficient and allows users or researchers to modify algorithms for their specific requirements. </p>

  <p><a class="zip_download_link" href="https://github.com/openconnectome/m2g/zipball/master">Download this project as a .zip file</a></p>
  
  <p><a class="tar_download_link" href="https://github.com/openconnectome/m2g/tarball/master">Download this project as a tar.gz file</a></p>

.. raw:: html

   <div class="container-fluid">
   <div class="row">
   <div class="col-md-4">
   <h2>Documentation</h2>

.. toctree::
   :maxdepth: 1

   docs/introduction
   docs/local_config
   docs/cluster_config
   docs/cloud_computing
   docs/contributing
   docs/style
   docs/faq
   Release Notes <https://github.com/openconnectome/m2g/releases/>

.. raw:: html

  </div>
  <div class="col-md-4">
  <h2>Tutorials</h2>
  
.. toctree::
   :maxdepth: 1

   tutorials/basic_usage
   tutorials/data
   tutorials/algorithms
   tutorials/validation
   tutorials/analysis

.. raw:: html

   </div>
   <div class="col-md-4">
   <h2>Further reading</h2>
   
.. toctree::
   :maxdepth: 1
   
   docs/functions
   Gitter chatroom <https://gitter.im/openconnectome/m2g>
   Mailing list <https://groups.google.com/forum/#!forum/ocp-support/>
   Github repo <https://github.com/openconnectome/m2g>
   Project page <https://openconnectome.github.io/m2g/>

.. raw:: html
   </div>
   </div>
   </div>

