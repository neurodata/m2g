m2g repo
==================
*This is file may be a bit out-of-date. It will be revisioned momentarily*

An easily integrable package that builds connectome graphs from derived data
products and gives the ability to compute invariants. This is a minimal subset of the [m2g repo](https://github.com/openconnectome/m2g).
The full repo includes code for web services that perform the same and additional operations - all found at [http://openconnecto.me/graph-services/](http://openconnecto.me/graph-services/).

This repo's code is currently used as a back-end plugin to the JHU-APL MIGRAINE pipeline for efficiently estimating connectomes.

TESTED ON:
------------
- 64-bit Linux Ubuntu 12.04 LTS
- 64-bit Linux CentOS 6.2
- 64-bit Mac OSX 10.7.5
- Should work with other Posix-like environments (possible tweaking required)

INSTALLATION INSTRUCTIONS:
==========================
Dependencies:
-------------
- [GNU R >= 3.0.2](http://www.r-project.org/)
- [igraph](http://igraph.sourceforge.net/) >= version 7.0 
  - C, R, Python 

- Add the following to your PYTHONPATH:
**If Install directory is ~/**
Add to ~/.bashrc:
<pre>
export PYTHONPATH=$PYTHONPATH:~/m2g/
export PYTHONPATH=$PYTHONPATH:$~/m2g/MROCPdjango/
</pre>

This can be done as follows:
<pre>
echo 'export PYTHONPATH=$PYTHONPATH:~/m2g/' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:~/m2g/MROCPdjango/' >> ~/.bashrc
</pre>

If install directory is different - replace '~' with the install directory path.

Clean install:
-------------
<pre>
# update & upgrade
apt-get update
apt-get upgrade

# Python installs
apt-get install python-dev
apt-get install python-setuptools
easy_install pip

# GCC compiler
apt-get install build-essential

# Cython
easy_install cython

# Numpy
sudo pip install numpy
exec bash

# Scipy
apt-get install libatlas-base-dev gfortran
easy_install scipy

# Matplotlib
apt-get install python-matplotlib

# Readline
apt-get install libreadline-dev

# Rpy2
easy_install rpy2

# argparse
easy_install argpase

# cd into the ../mrcap directory.
# Build cython zindex module
python setup.py install

# igraph
Follow instructions posted at http://igraph.sourceforge.net/doc/html/igraph-installation.html

# nibabel
easy_install nibabel

</pre>

The following should be installed when you are done:
- pip
- easy_install
- Python 2.7
- gcc compiler
- gfortran 77 compiler
- Cython version 0.16
- Scipy version 0.10.1
- Numpy version 1.5.1
- Matplotlib version 1.1.1rc
- zindex cython module
- argparse
- Readline
- rpy2 
- nibabel

Examples:
=========

INSTALLDIR=$(pwd) # *NOTE if install dir is different alter this.*
Example located in <pre>INSTALLDIR/m2g/MROCPdjango/computation/composite/examples</pre>

Once in example directory, Simply type: `./example.sh`
This will run **small graph** generation code & 6 invariant computations.
opening the `example.sh` file and uncommenting other lines can be done to run the same code, but for a big graph and largest connected component.

Documentation:
==============
pydoc can be run for the entire project using the executable python script:
<pre>./INSTALLDIR/m2g/docgenerator</pre>
The resulting html can be found in *INSTALLDIR/m2g/doc* (unless otherwise specified so with a command line flag)
For help type: `/INSTALLDIR/m2g/docgenerator -h`

Integration test:
=================
A single test is available in *INSTALLDIR/m2g/* to test all modules will compile. The only way to test for runtime errors "out of the box" is to run the example script as noted above. The integration test can be invoked via ./INSTALLDIR/m2g/docgenerator. The script all scripts in the package with helpful info. If an error is encountered you will be prompted to continue or stop to fix the error!
To run the test type:
<pre>
./INSTALLDIR/m2g/intergrtest
</pre>

Finally - enjoy!
Problems: Contact us at: jhu.mrocp@cs.jhu.edu
Thanks
