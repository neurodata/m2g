This is the homepage for the Magnetic Resonance Connectome Automated Pipeline (MRCAP). &nbsp;The alpha version of our code has now been released. &nbsp;If you would like to be notified of our next release, or for more information, please contact Will Gray (willgray@jhu.edu). &nbsp;A manuscript that describes the methods used in MRCAP is available in a recent issue of [http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=6173097 IEEE Pulse]. 

== <span class="Apple-style-span" style="font-size: 18px; font-weight: bold;">MRCAP Overview</span>  ==

MRCAP combines diffusion tensor imaging (DTI or dMRI) and structural (MPRAGE or sMRI) data from a single subject to estimate a high-level connectome, which is a description of the wiring diagram of the brain. &nbsp;MRCAP is efficient and its modular construction allows researchers to modify algorithms to meet their specific requirements. The pipeline has been validated and over 200 connectomes have been processed and analyzed to date. <br> 

Conceptually, the pipeline is divided into three parts: &nbsp;a diffusion layout, structural layout, and connectivity layout. &nbsp;The diffusion layout estimates tensors and computes fiber tracts based on the FACT algorithm. &nbsp;The structural layout preprocesses the volume and performes gyral labeling based on the Desikan structural parcellation. &nbsp;Finally, the connectivity layout coregisters the two image volumes and estimates the connectivity between each of the regions. &nbsp;Additional details can be found in our manuscript, which is in press and will be added online, shortly. &nbsp; 

<br> 

[[Image:Mrcap:MRCAP pipeline overview v1 0 small.jpg|MRCAP Pipeline Overview]] 

''MRCAP Pipeline Overview''<br> 

== Requirements  ==

In order to install and use the MRCAP processing pipeline, MIPAV and JIST have to first be installed on your system. &nbsp;Certain versions of MIPAV and JIST are '''required''' to ensure that the pipeline operates correctly.&nbsp; 

MIPAV and JIST are Java-based, and can be run on a wide variety of platforms (e.g., Windows, Mac, Linux). 

In order to run the algorithms, it is recommended that each subject is allocated one processor core (2GHz+) and 10GB of RAM. &nbsp;It may be possible to run the pipeline with fewer resources, but users in this situation should contact us for more information. &nbsp; 

== Installation Instructions<br>  ==

This section explains how to successfully install and configure MRCAP and its associated dependencies. ''&nbsp;All software is available as a link from our download page.''<br> 

=== Install MIPAV '''Version 5.3.1'''&nbsp;  ===

MIPAV&nbsp;(Medical Image Processing, Analysis, and Visualization)&nbsp;is an imaging and processing tool that provides the foundation for JIST and MRCAP. &nbsp;The software is directly available from&nbsp;http://mipav.cit.nih.gov/. &nbsp;Note that archival releases are at the bottom of the Downloads page. &nbsp;Installation instructions are provided on the MIPAV site and are not reproduced, here. 

=== Download JIST+CRUISE, nightly build 06/28/2011. &nbsp;  ===

This software provides the modules required to run MRCAP, and the JIST plugin for MIPAV. &nbsp;To ensure correct pipeline performance, users must use the specified version of JIST. &nbsp;It is possible to install many versions of JIST side-by-side on the same system. &nbsp;It is not necessary to do any installation of JIST into MIPAV or additional setup, beyond unpacking the JIST-CRUISE .JAR file into a new directory. &nbsp;To unpack the JAR file, navigate to a clean subdirectory and simply type: &nbsp;unzip JIST-CRUISE<br> 

=== Download the MRCAP Jist layout (Version 0.8 Alpha)  ===

Download the XML MRCAP layout file and the startMRCAP script. &nbsp;The startMRCAP script includes all necessary entries on the classpath and starts JIST. &nbsp;It will need to be modified to reflect the correct locations on your system. &nbsp;The file content is as follows: 

<br> 

&lt;mipav_directory&gt;/jre/bin/java -Xmx3000m -classpath "&lt;mipav_directory&gt;:&lt;mipav_directory&gt;/jre/lib/*:&lt;mipav_directory&gt;/jre/lib/*/*:&lt;mipav_directory&gt;/lib/*:&lt;mipav_directory&gt;/lib/*/*:&lt;mipav_directory&gt;/InsightToolkit/lib/InsightToolkit/InsightToolkit.jar:&lt;JIST+CRUISE_directory&gt;" StartJIST 

<br> 

&lt;mipav_directory&gt; points to the top-level directory where you installed mipav &nbsp;(e.g. &nbsp;/home/wgray/mipav531) 

&lt;JIST+CRUISE_directory&gt; is the directory where you unpacked the JIST+CRUISE JAR<br> 

Note that on a Macintosh computer, Java is controlled by the OS, and will likely reside in a separate location (e.g. /usr/bin/java) 

== ''<span class="Apple-style-span" style="font-style: normal;">Usage Guidelines</span>''  ==

''This section describes how to run the MRCAP pipeline. &nbsp;''Briefly, the inputs are the strengths (b-values) and directions (gradients) of the DTI scans, as well as the overall DTI (dMRI) and MPRAGE (sMRI) image volumes. The outputs are two connectivity matrices (or connectomes), based on fiber count and mean(meanFA). &nbsp;The atlases used by default in MRCAP parcellate the brain into 70 regions, so the connectivity matrices have roughly 2500 (70 x 70 / 2)&nbsp;undirected edges. &nbsp; 

<br> 

Any native MIPAV formats (e.g. Nifti, XML/RAW) are supported. &nbsp;It is preferred that DICOM formats are converted to a more compact format. &nbsp;MRI Convert (http://lcni.uoregon.edu/~jolinda/MRIConvert/) is an excellent, free tool. 

<br> 

Once you have launched JIST, go to file, open, and select the MRCAP_template file. &nbsp;The input should be organized by subject (templates provided) in a CSV or TXT file. &nbsp;The template layout is designed to run multiple subjects; however, a single subject can be processed using the above approach, if desired. &nbsp;It is possible to customize the layouts to suit your data's specific format and algorithm requirements. &nbsp;More information on customization will be provided as part of the Beta MRCAP release, expected in late July. &nbsp; 

<br> 

Once the input text files have been created, select them by specifying the parameters in the JIST input modules (blue). &nbsp;Once all four inputs have been specified, go to Project, Layout Preferences. &nbsp;You should specify a high-level output path for your results (the directory will be created if necessary). &nbsp;Heap size (at least 10GB) and simultaneous processes (at least 1) should reflect your processing hardware capabilities. Next, go to Project, Global Preferences. &nbsp;Select a new directory for your module library, (e.g., ../mrcap/library). &nbsp;Rebuild your library. 

<br> 

Prior to running, ensure that the configuration files in the VABRA, SPECTRE, and Atlas Registration Modules are set correctly. &nbsp;(Will be updated 6/30.) 

<br> 

Finally, go to Project, Processing Manager, and wait for your experiment(s) to load. &nbsp;Click on Start Scheduler to process your data. &nbsp;Additional instructions and screenshots will be provided, soon.<br> 

<br> 

JIST provides native capabilities to process a number subjects in parallel (typically 1 per computer core is an appropriate loading, given 10 GB of available RAM per core). &nbsp;Example input files are provided; subject input file information should be stored in .txt or .csv files and specified in the input modules of the layout. &nbsp;<br><br>Simple archival and post-processing analysis scripts are also made available to the user community.<br> 

== Potential Applications  ==

Connectomes can be used for a variety of applications and classification tasks. &nbsp;Our team uses the output information to develop and test statistical graph-theoretical classification methods.<br> 

== More Information/Where to Get Help  ==

'''''For more information, or to get help, please contact Will Gray (willgray@jhu.edu) or Joshua Vogelstein (joshuav@jhu.edu).'''''
