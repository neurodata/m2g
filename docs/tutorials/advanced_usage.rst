Advanced Usage
**************
The code blocks below act as a walkthrough of how to run the m2g pipeline incrementally. Before beginning, please ensure that you have installed the pipeline either locally or on a cluster, and have checked out the basic usage page. Timing estimates are also provided based on how long it takes on a desktop machine with 64 GB of RAM and 12 virtual CPU cores. Evaluating the pipeline for a single subject will, at it's peak, consume approximately 4 GB of RAM and fully load 2 CPU cores.

**Data Path**

Before beginning processing, it is often convenient to establish some system variables that keep track of where you will be grabbing/pushing data throughout the pipeline. In this case, we're assuming that you are using the MNI152 atlas provided in m2g, as well as the desikan labels, that your raw data is stored in the /data directory, and that M2G_HOME variable has already been set during setup.

.. code-block:: bash

	M2G_HOME=/mrimages/src/m2g
	#Working output directory
	DATA=/data
	#Structural image
	MPRAGE=/data/MPRAGE.nii
	#Diffusion image and scanner params
	DTI=/data/DTI.nii
	BVAL=/data/DTI.b
	BVEC=/data/DTI.bvec
	#Atlas image and labels
	MNI=${M2G_HOME}/data/Atlas/MNI152_T1_1mm.nii.gz
	MASK=${M2G_HOME}/data/Atlas/MNI152_T1_1mm_brain_mask.nii
	LABELS=${M2G_HOME}/data/Atlas/MNI152_T1_1mm_desikan_adjusted.nii

DTI Preprocessing
~~~~~~~~~~~~~~~~~

**Parse B values**

In order to identify where the B0 volume is in the DTI image stack, the B-value intensity of the non-B0 scans, and properly format the gradient files to be compatible with our tensor estimation, we must first parse these files directly. LONI will automatically string parse the outputs to command line of these values, but as you are running this manually you will need to manually store them in variables. Expect this to take under a second.

.. code-block:: bash

	BVEC_NEW=${DATA}/new.bvec
	python2.7 ${M2G_HOME}/packages/dtipreproc/parse_b.py ${BVAL} ${BVEC} ${BVEC_NEW}
	#in our dataset we saw the following:
	B=700
	B0=32

**Extract B0**

Once we know the location of the B0 volume, we are able to extract it from the DTI image stack. This will be used for aligning the DTI volumes to the structural MPRAGE volume. Expect this to take approximately a second.

.. code-block:: bash

	B0_vol=${DATA}/B0volume.nii.gz
	python2.7 ${M2G_HOME}/packages/dtipreproc/extract_b0.py ${DTI} ${B0} ${B0_vol}

**Eddy Correction**

Before processing our diffusion data, we perform both chromatic alignment and internal spatial alignment. In other words, we correct for noise in the image acquisition as well as align all of the DTI volumes to each other. This will take different amounts of time depending on the number of diffusion directions in your image. For instance, if there are 34 diffusion directions this takes approximately 22 minutes.

.. code-block:: bash

	DTI_aligned=${DATA}/DTI_aligned.nii.gz
	eddy_correct ${DTI} ${DTI_aligned} ${B0}

Registration
~~~~~~~~~~~~

**Register B0 to MPRAGE; MPRAGE to Atlas**

In parallel to aligning the DTI volumes, we compute the transform that will register the B0 volume - and effectively the entire DTI stack - to the MPRAGE image, and then from the MPRAGE space to your atlas space. Each registration takes approximately 10 minutes to complete.

.. code-block:: bash

	B0_in_MP=${DATA}/B0_in_MPRAGE.nii.gz
	txm1=${DATA}/b0_mp.xfm
	flirt -in ${B0} -ref ${MPRAGE} -out ${B0_in_MP} -omat ${txm1} -cost normmi -searchrx -180 180 -searchry -180 180 -searchrz -180 180

	MP_in_MNI=${DATA}/MPRAGE_in_MNI.nii.gz
	txm2=${DATA}/mp_mni.xfm
	flirt -in ${MPRAGE} -ref ${MNI} -out ${MP_in_MNI} -omat ${txm2} -cost normmi -searchrx -180 180 -searchry -180 180 -searchrz -180 180

**Apply registration to DTI**

The transforms which were computed in the previous step are now applied to the 4D DTI volume, concluding the preprocessing of the DTI data. Applying the transforms to the DTI volume stack takes approximately 3 minutes for an image with 34 diffusion directions.

.. code-block:: bash

	DTI_in_MP=${DATA}/DTI_in_MPRAGE.nii.gz
	DTI_in_MNI=${DATA}/DTI_in_MNI.nii.gz
	flirt -in ${DTI_aligned} -ref ${MPRAGE} -out ${DTI_in_MP} -init ${txm1} -applyxfm -paddingsize 0.0

	flirt -in ${DTI_in_MP} -ref ${MNI} -out ${DTI_in_MNI} -init ${txm2} -applyxfm -paddingsize 0.0

Diffusion Processing
~~~~~~~~~~~~~~~~~~~~

**Tensor estimation**

The first step in processing diffusion data is to estimate tensors at each voxel. This will compress the 4D DTI images into a single 3D image with a tensor at each voxel. Expect tensor estimation to take approximately 5 minutes.

.. code-block:: bash

	SCHEME=${DATA}/scheme.scheme
	DTI_BFLOAT=${DATA}/DTI.Bfloat
	TENSORS=${DATA}/DTI_tensors.Bdouble
	python2.7 ${M2G_HOME}/packages/tractography/tensor_gen.py ${DTI_in_MNI} ${BVEC_NEW} ${B} ${MASK} ${SHEME} ${DTI_BFLOAT} ${TENSORS}

**Fiber tractography**

The tensors computed in the prevoius step are traversed and fiber tracts, or streamlines, are formed. This step takes quite a long time, and the status can be monitored by viewing the log file with the cat command. This step is by far the slowest in the pipeline, and you should expect it to take approximately 1-2 hours. If you're computing this remotely via ssh, it is recommended to use the screen command to avoid being disconnected.

.. code-block:: bash

	FIBERS=${DATA}/fibers.Bfloat
	VTK=${DATA}/fibers.vtk
	LOG=${DATA}/logfile.log
	python2.7 ${M2G_HOME}/packages/tractography/fiber_gen.py ${TENSORS} ${MASK} 0.2 70 ${FIBERS} ${VTK} ${LOG}

**Fiber conversion**

The format of the fibers produced by Camino in the previous step is incompatible with the graph generation code which we use, so the format must be converted as follows. Converting fiber formats should take approximately 2 minutes.

.. code-block:: bash

	FIBERS_NEW=${DATA}/fibers.dat
	python2.7 ${M2G_HOME}/packages/tractography/fiber_convert.py ${FIBERS} ${FIBERS_NEW}

**Graph generation**

The fibers are tracked through the brain and edges are added to a graph. For each region a fiber passes through, an edge is added in the adjacency matrix. Graph generation should take approximately 5-10 minutes.

.. code-block:: bash

	GRAPH=${DATA}/graph.graphml
	python2.7 ${M2G_HOME}/MR-OCP/mrcap/gengraph.py ${FIBERS_NEW} ${LABELS} ${GRAPH} --outformat graphml -a ${LABELS}

**Graph conversion**

If you prefer to work with graphs in the matlab compatible mat format, then run this conversion script which will parse the graphml for you. Graph conversion should take less than 1 minute.

.. code-block:: bash

	GRAPH_NEW=${DATA}/graph.mat
	python2.7 ${M2G_HOME}/packages/utils/graphml2mat.py ${GRAPH} ${GRAPH_NEW}

