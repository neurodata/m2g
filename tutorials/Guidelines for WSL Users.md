# NDMG Installation Steps for Windows Users
## Set up WSL (Windows Subsystem for Linux)
Purpose: to enable the WSL function on your computer
Steps: 
--- open 'Control Panel'
--- click 'Programs'
--- click 'Turn Windows features on or off'
--- click 'Windows Subsystem for Linux' on
--- click 'OK'
## Install GUI Xming
Purpose: to install a GUI tool for Linux Subsystem and Ubuntu
Notes: 
There are different kinds of GUIs like VcXsrv, but VcXsrv (Xlaunch) cannot open fsleyes in the following steps, so please do install Xming!
Steps: 
--- open https://sourceforge.net/projects/xming/
--- click 'Download'
--- run 'Xming-[xxxx-version]-setup.exe'
--- follow the installation steps and click 'next' on
--- complete installation
## Install Ubuntu
Purpose: to download Ubuntu as a terminal for your Linux Subsystem
Steps:
--- open https://ubuntu.com/download/desktop and download (version 18.04 recommended)
--- launch 'Ubuntu'
--- now you can use it as a terminal and install git, lfs, python, pip…
Note: check the version of python in Ubuntu, if there is no Python2.7 currently, install it in the terminal:
```sh
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install python2.7 python-pip
$ sudo apt install python3-pip
```
## Install AFNI
Purpose: ndmg use the skull-strip module from AFNI.
Steps:
Please follow the steps on 'https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/steps_windows10.html'
## Install FSL
Purpose: ndmg pipelines use fsl in several steps.
Notes: the 'fslinstaller.py' should be run using python2!
Steps:
--- open 'https://fsl.fmrib.ox.ac.uk/fsl/fslwiki'
--- click 'Download and Installation' and follow the steps provided
## Run the NDMG pipeline
Purpose: to check if the steps above are completed and run the pipeline for the first time!
Steps:
```
git clone https://github.com/neurodata/ndmg.git
cd ndmg; git checkout staging
pip install -r requirements.txt
pip install .
ndmg_bids --atlas desikan </absolute/input/dir> </absolute/output/dir>
```