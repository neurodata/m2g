.. M2G is kinda good.
.. meta::
   :description: Official documentation for M2G:  MR Images to Graphs 
   :keywords: MRI, pipeline, neuroscience, diffusion, resting state
.. title::
   m2g

.. raw:: html

	<h1>m2g:  Framework for robust, reliable MR connectome estimation</h1>
	<br>

.. raw:: html

    <div style="clear: both"></div>
    <div class="container-fluid hidden-xs hidden-sm">
      <div class="row" align="center">
        <a>
            <img class="mythumbnail" src="_static/mprage.png" height="125" width="125">
        </a>
        <a>
            <img class="mythumbnail" src="_static/fmri.png" height="125" width="125">
        </a>
        <a>
            <img class="mythumbnail" src="_static/dti.png" height="125" width="125">
        </a>
        <a>
            <img class="mythumbnail" src="_static/fibers.png" height="125" width="125">
        </a>
        <a>
            <img class="mythumbnail" src="_static/graph.png" height="125" width="125">
        </a>
      </div>
    </div>
    <br>

.. raw:: html

  <hr>
  <p>This page describes how brain graphs are generated in our service from Diffusion Weighted MRI (dMRI), and structural MRI (sMRI) images of human brains, as well as a template atlas (MNI152, for instance). The MRImages to Graphs (m2g) pipeline is the successor of MRCAP and MIGRAINE. m2g combines dMRI and sMRI data from a single subject to estimate a high-level connectome. The connectomes returned describe regions of connectivity within the brain at multiple levels of resolution in the form of a graph - where a node ranges from a single voxel scale ~1 mm<sup>3</sup> to large cortical regions ~20 cm<sup>3</sup>.</p>

  <p> m2g has been developed in the LONI pipelining environment. This environment facilitates modular construction, and all workflows and modules are command-line executable. This makes m2g efficient and allows users or researchers to modify algorithms for their specific requirements. </p>
  
  <p>We are currently processing brain scans, and the resulting graphs are made available to the community on an ongoing basis. </p>

.. raw:: html
 
  <div>
    <img style="width:30px;height:30px;vertical-align:middle">
    <span style=""></span>
    <IMG SRC="_static/GitHub.png" height="50" width="50"> <a ref="https://github.com/openconnectome/m2g/zipball/master"> [ZIP]   </a>  
    <a image="_static/GitHub.png" href="https://github.com/openconnectome/m2g/tarball/master">[TAR.GZ] </a></p>
  </div>


.. sidebar:: m2g Contact Us 
   
   If you have questions about m2g, or have data to process, let us know:  m2g-support@openconnecto.me
   
.. toctree::
   :maxdepth: 1
   :caption: Documentation

   sphinx/introduction
   sphinx/local_config
   sphinx/cloud_computing
   sphinx/ocp
   sphinx/faq

.. toctree::
   :maxdepth: 1
   :caption: Tutorials

   tutorials/input_data
   tutorials/available_data
   tutorials/basic_usage
   tutorials/advanced_usage
   tutorials/validation

.. toctree::
   :maxdepth: 1
   :caption: Further Reading

   api/functions
   api/modules
   Web service <http://ocp.me/graph-services/c4/>
   Gitter chatroom <https://gitter.im/openconnectome/m2g>
   Mailing List <https://groups.google.com/a/ocp.me/forum/#!forum/m2g> 
   Github repo <https://github.com/openconnectome/m2g>
   Release Notes <https://github.com/openconnectome/m2g/releases/>

If you use m2g or its data derivatives, please cite:
   G Kiar, W R Gray Roncal, D Mhembere, R Burns, JT Vogelstein (2015). m2g v1.1.1. Zenodo. 10.5281/zenodo.18066 `zenodo <https://zenodo.org/record/18066#.VWaPfFxViko>`_ `bibtex <http://openconnecto.me/data/public/MR/m2g_v1_1_0/m2gv111.bib>`_

   W Gray Roncal, ZH Koterba, D Mhembere, DM Kleissas, JT Vogelstein, R Burns, AR Bowles, DK Donavos, S Ryman, RE Jung, L Wu, V Calhoun, RJ Vogelstein. MIGRAINE: MRI Graph Reliability Analysis and Inference for Connectomics. GlobalSIP, 2013 `arXiv <http://arxiv.org/abs/1312.4875>`_ `bibtex <http://openconnecto.me/data/public/MR/MIGRAINE_v1_0/migraine.bib>`_

  
