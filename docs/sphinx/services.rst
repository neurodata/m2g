Services
********

Using m2g on captive cluster
----------------------------
In order to run m2g on the captive cluster we run in house (braincloud1), we expect you to have the following requirements satisfied:

1. A LONI client installed on your client computer that is the compatible version to our sever (Currently v6.0). Contact LONI and `request a copy <http://pipeline.loni.usc.edu/learn/contact/>`_, as this is not the most recent release and they don't publicly share older versions.

2. Your data organized in compliance with our `input specification <http://m2g.io/tutorials/data.html>`_

3. An account on the cluster. If you don't have an account and would like one, you can email `support@neurodata.io <mailto:support@neurodata.io>`_ to see if you're eligible.

**Moving your data:**

* scp/rsync or equivalently move your data to ``braincloud1:/brainstore/MR/``
* ensure that the data directory is readable and writeable by user pipeline. An example of this is done below

.. code-block:: none

  rsync -rv --progress /path/to/mydata ${user}@braincloud1.cs.jhu.edu:/brainstore/MR/mydata
  ssh ${user}@braincloud1.cs.jhu.edu
  cd /brainstore/MR/mydata
  chmod -R 775 ./

**Processing your data:**

* On your computer, open the LONI client and connect to braincloud1
* Open the m2g workflow found in your local cloned copy of the m2g repo at subdirectory ``library/workflows/m2g_lists.pipe``
* Open the variables dialog from the wrench on the top right. The ``inputDir`` variable should be set to the location of your data. The ``outputBaseDir`` should be the location you would like derivates to be stored. The ``sglabels`` variable points to a file which contains a list of parcelations to process your data with. You can open this file on braincloud to see the atlases chosen, and if you wish to adjust the atlases used you can create a new file in your data directory containing paths to the atlases you wish to use (if they don't exist in m2g already, you will need to copy them as well like was done above). If you wish to process in a space other than the MNI152 template, then you will also need to provide new paths for the remaining variables to the atlas space you wish to use.
* Press run
* Find your `graphs and other derivatives <http://m2g.io/tutorials/data.html#output-data>`_ from the base directory you provided
* Enjoy!

Using m2g in an AMI
-------------------
Before beginning this guide, please ensure that you have the following:

1. Amazon AWS credentials

2. Your data organized in compliance with our `input specification <http://m2g.io/tutorials/data.html>`_

**Creating and connecting to the workstation:**

* Log in to the AWS Console and navigate to EC2 services
* Create new EC2 instance. If you are unfamiliar with this, the following `guide <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html>`_ may be useful to use in concert with ours. This will also be useful when mounting a harddrive, as you'll be doing shortly.
* Under 'Community AMIs' search for ``neurodata`` and select the most recent version
* Proceed to select computer size, storage, and security preferences, and launch instance. The computer size should be proportional to the amount of data you are wishing to run. Larger instances are suggested for faster performance, though smaller instances (must have > 8GB of RAM) are good for debugging and test runs of your data. Storage is also proportional to your data needs. It is suggested that your additional storage is at least twice the size of your dataset, to ensure room for data derivatives. The default security settings are often sufficient, though if you have privacy concerns for your data you should contact AWS Support and see how to make your instance HIPPA compliant
* Once your instance is online, initiate an SSH tunnel through a terminal on your computer by running the following command with your ip address. You will be prompted to enter the password ``neurodata``:

.. code-block:: none

  ssh -L 5901:127.0.0.1:5901 -N -f -l neurodata ${ip}

* Open a VNC client like `RealVNC <https://www.realvnc.com/products/chrome/>`_. For Mac users, screenshare is built in and has this capability.
* Connect to 127.0.0.1:5901 and enter the password ``neurodata``
* Login to the workstation using the same password

**Processing your data:**

* Mount an addtional harddrive with sufficient storage capacity for your data. This can be done through the same `guide <http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html>`_ that helped you start your instance
* Move all of your data into your new harddrive (either through s3, or scp or equivalent). If you don't have your own data and wish to download `publicly available datasets <http://m2g.io/tutorials/available_data.html>`_ you may download them directly to the EC2 instance. An example of transfering data from your computer can be done in the terminal of your client computer as follows:

.. code-block:: none

  scp -r /path/to/your/data/ ${ip}/data/

* Create a ``temp`` directory on this new harddrive, as well
* Open terminal and type the following:

.. code-block:: none

  cd /share0/m2g/
  git pull
  cd /share0/src/loni/loni_6.0.1
  ./PipelineGui.sh
  
* A LONI Pipeline window will open. Decline any prompts to update this client upon load
* Open the m2g workflow, located at `/share0/m2g/library/m2g_sources_bc1_v4.pipe`
* In LONI, open the ``Edit > Preferences`` menu
* Change the Pipeline Cache to the ``temp`` folder you created earlier. Be sure that directory has permissions ``777``
* Change the number of simultaneous jobs in Local Execution to be approximately 90-95% of the total cores in your instance
* Open the variables dialog from the wrench on the top right. The ``inputDir`` variable should be set to the location of your data. The ``outputBaseDir`` should be the location you would like derivates to be stored. The ``sglabels`` variable points to a file which contains a list of parcelations to process your data with. You can open this file on braincloud to see the atlases chosen, and if you wish to adjust the atlases used you can create a new file in your data directory containing paths to the atlases you wish to use (if they don't exist in m2g already, you will need to copy them as well like was done above). If you wish to process in a space other than the MNI152 template, then you will also need to provide new paths for the remaining variables to the atlas space you wish to use.
* Press run
* Find your `graphs and other derivatives <http://m2g.io/tutorials/data.html#output-data>`_ from the base directory you provided
* Enjoy!

Downloading Graphs
------------------

Our graph service engine, `MROCP <http://mrbrain.cs.jhu.edu/graph-services/welcome/>`_, hosts graph data of a variety of species and scales, as well as enables downsampling and type conversion of graphs.

