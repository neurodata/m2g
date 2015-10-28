Cloud Services
**************

There are several options when using m2g in the cloud. We provide a user-facing preconfigured AMI on the Amazon Community Marketplace for users to access and launch, as well as host graph services users can access for direct data downloads. In the near future, an additional web service which allows users to simply supply an s3 bucket to us and received processed derivatives in return will be available - stay tuned.

Using m2g in an AMI
-------------------
Before beginning this guide, please ensure that you have the following:
1. Amazon AWS credentials
2. Your data organized in compliance with our `input specification <http://m2g.io/tutorials/input_data.html>`_

**Creating and connecting to the workstation:**

* Log in to the AWS Console and navigate to EC2 services
* Create new EC2 instance
* Under 'Community AMIs' search for 'neurodata' and select the most recent version
* Proceed to select computer size, storage, and security preferences, and launch instance
* Once your instance is online, initiate an SSH tunnel through a terminal on your computer by running the following command with your ip address. You will be prompted to enter the password `neurodata`:

.. code-block:: none

  ssh -L 5901:127.0.0.1:5901 -N -f -l neurodata ${ip}

* Open a VNC client like RealVNC https://www.realvnc.com/products/chrome/
* Connect to 127.0.0.1:5901 and enter the password `neurodata`
* Login to the workstation using the same password

**Processing your data:**

* Move all of your data into your workstation (either through s3, or scp or equivalent). If you don't have sufficient space then you may need to attach an additional harddrive during creation of your instance.
* Open terminal and type the following:

.. code-block:: none

  cd /share0/m2g/
  git pull
  cd /share0/src/loni/loni_6.0.1
  ./PipelineGui.sh
  
* A LONI Pipeline window will open. Decline any prompts to update this client upon load.
* Open the m2g workflow, located at `/share0/m2g/library/m2g_sources_bc1_v4.pipe`
* Change variable to the base directory of your data
* Press run
* Find your graphs and other derivatives from the base directory you provided
* Enjoy!

Downloading Graphs
------------------

Our graph service engine, `MROCP <http://mrbrain.cs.jhu.edu/graph-services/welcome/>`_, hosts graph data of a variety of species and scales, as well as enables downsampling and type conversion of graphs.

