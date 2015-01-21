<h1 >MIGRAINE</h1>
<h2>MRI Graph Reliability Analysis and Inference for Connectomics</h2>
<h3>Description</h3>
<h3>Installation</h3>
<h5>MRCAP</h5>

<h5>MIGRAINE</h5>
<hr/>

<h5>Required Libraries</h5>

<ul>
	<li>Python 2.7</li>
	<li>MIPAV 5.3.1</li>
	<li>MatLab [Latest]</li>
	<li>LONI [Latest]</li>
	<li>JIST CRUISE 2012: Jan29-11-11PM</li>
</ul>

<h5>Version 1.0.1 Installation Steps</h5>

<ol type="1">
  <li>Install above libraries/software so that it is accessible by all clusters</li>
  <li>Replace JIST files</li>
  	<ol type="i">
  <li>Replace [JIST Location]/edu/jhu/ece/iacl/jist/cli/run.class with run.class in /install/jistreplacements/</li>
  <li>Replace [JIST Location]/edu/jhu/ece/iacl/jist/cli/run.class with run.class in /install/jistreplacements/</li>
</ol>
<li>Open main migraine pipleine with LONI client: /migraine/workflows/migraine_1_01.pipe</li>
<li>Modify Variables</li>
  	<ol type="i">
  <li>Modify classP:</li>
[MIPAV Directory]:[MIPAV Directory]/lib/*:[MIPAV Directory]/lib/*/*:[MIPAV Directory]/InsightToolkit/lib/InsightToolkit/InsightToolkit.jar:[JIST Directory]/library/*:[JIST Directory]
  <li>Modify shareP:</li>
  [Installation Directory]
</ol>
<li>Modify data sources</li>
<li>Run</li>
</ol>

<h3>References</h3>