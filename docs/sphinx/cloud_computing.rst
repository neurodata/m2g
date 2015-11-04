Cloud Services
**************

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

* Mount an addtional harddrive with sufficient storage capacity for your data
* Move all of your data into your new harddrive (either through s3, or scp or equivalent)
* Create a `temp` directory on this new harddrive, as well
* Open terminal and type the following:

.. code-block:: none

  cd /share0/m2g/
  git pull
  cd /share0/src/loni/loni_6.0.1
  ./PipelineGui.sh
  
* A LONI Pipeline window will open. Decline any prompts to update this client upon load
* Open the m2g workflow, located at `/share0/m2g/library/m2g_sources_bc1_v4.pipe`
* In LONI, open the `Edit > Preferences` menu
* Change the Pipeline Cache to the `temp` folder you created earlier. Be sure that directory has permissions `777`
* Change the number of simultaneous jobs in Local Execution to be approximately 90-95% of the total cores in your instance
* Open the variables dialog from the wrench on the top right, and change the variables to point to your data and where you want your derivatives stored
* Press run
* Find your graphs and other derivatives from the base directory you provided
* Enjoy!

Downloading Graphs
------------------

Our graph service engine, `MROCP <http://mrbrain.cs.jhu.edu/graph-services/welcome/>`_, hosts graph data of a variety of species and scales, as well as enables downsampling and type conversion of graphs.

