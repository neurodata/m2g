Setup
*****

m2g requires the following packages:  python2.7, igraph, numpy, scipy, Oracle Java, R, LONI Pipeline, FSL, and Camino. Specific installation instructions are provided here for Centos 6.X. We do not currently provide support for other operating systems.

Basic Package Update and Install
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  export m2g=/mrimages #root directory
  yum update -y
  yum install -y wget gcc elfutils-libelf-devel libstdc++-devel glibc-devel libaio-devel gcc-c++
  yum groupinstall -y "Development tools" "X Window System" "Fonts"
  yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel xz-devel


Install and Configure Python 2.7 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

  	wget http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
	tar xf Python-2.7.6.tar.xz
	cd Python-2.7.6
	./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
	make && make altinstall

	# Make python 2.7 default 
	export PATH='/usr/local/bin':${PATH}
	ln -s /usr/local/bin/python2.7 /usr/local/bin/python
	# First get the setup script for Setuptools:
	wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
	# Then install it for Python 2.7:
	python2.7 ez_setup.py
	easy_install-2.7 pip

Basics for Development
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

	#Basics for development
	yum install -y java-1.6.0-openjdk-devel cmake vim screen
	yum install -y bc
	yum install -y epel-release
	yum install -y R
	pip2.7 install numpy
	pip2.7 install ipython
	pip2.7 install scipy

	easy_install-2.7 argparse
	easy_install-2.7 -U distribute
	yum -y install libpng-devel
	pip2.7 install scikit-image
	pip2.7 install nibabel
	pip2.7 install Cython # requires >= v0.22 

Oracle Java Install
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

	# Oracle Java Install
	mkdir -p $m2g/src/java
	cd $m2g/src/java
	wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/7u71-b14/jdk-7u71-linux-x64.tar.gz"
	tar xzf jdk-7u71-linux-x64.tar.gz
    
	cd $m2g/src/java/jdk1.7.0_71/
	alternatives --install /usr/bin/java java $m2g/src/java/jdk1.7.0_71/bin/java 2 
	alternatives --config java #MANUAL STEP:  type 2

Java Setup
~~~~~~~~~~~~~~

.. code-block:: bash

	alternatives --install /usr/bin/javac javac $m2g/src/java/jdk1.7.0_71/bin/javac 2
	alternatives --set javac $m2g/src/java/jdk1.7.0_71/bin/javac
	alternatives --install /usr/bin/jar jar $m2g/src/java/jdk1.7.0_71/bin/jar 2
	alternatives --set jar $m2g/src/java/jdk1.7.0_71/bin/jar

Camino and FSL 
~~~~~~~~~~~~~~

.. code-block:: bash

	#Camino
	cd $m2g/src
	git clone git://git.code.sf.net/p/camino/code camino
	cd camino
	make
	git checkout voxelSpaceStreamlines
	make clean
	make

	#FSL
	# Requires completing a form on the FSL website, running 
	# fslinstaller.py. We've stored the obtained binary on
	# a server for convenience.
	# FSL website: http://fsl.fmrib.ox.ac.uk/fsldownloads/
	cd $m2g/src/
	wget http://openconnecto.me/data/public/MR/m2g_v1_1_0/deps/fsl-5.0.8-centos6_64.tar.gz
	tar zxvf fsl-5.0.8-centos6_64.tar.gz
	#Delete raw targz if space is tight

igraph
~~~~~~~~

.. code-block:: bash

	# igraph
	yum -y install xml2 libxml2-devel
	cd ${m2g}/src
	wget http://igraph.org/nightly/get/c/igraph-0.7.1.tar.gz
	tar xvfz igraph-0.7.1.tar.gz
	cd igraph-0.7.1
	./configure --prefix=${m2g}/src/igraph
	make
	make install

	git clone https://gist.github.com/15015a9485d87d8c22e6.git
	cd 15015a9485d87d8c22e6
	Rscript installRigraph.R # using mirror: 'http://ftp.ussg.iu.edu/CRAN/src/contrib/igraph_0.7.1.tar.gz'
	cd ..
	rm -rf 15015a9485d87d8c22e6
m2g setup
~~~~~~~~~

.. code-block:: bash

	easy_install-2.7 python-igraph

	# Need to actually clone repo and install LONI
	# Also need to SCP data 
	cd ${m2g}/src
	git clone https://github.com/openconnectome/m2g.git
	cd m2g
	git checkout master #TODO

	export M2G_HOME=${m2g}/src/m2g

	cd $M2G_HOME/MR-OCP/mrcap
	python setup.py install #for z-index

	python $M2G_HOME/packages/utils/setup.py

	mkdir $m2g/data
	cd $m2g/data
	wget http://openconnecto.me/data/public/MR/m2g_v1_1_0/deps/KKI2009-22.tar.gz
	tar zxvf KKI2009-22.tar.gz

	cd $m2g/src
	wget http://openconnecto.me/data/public/MR/m2g_v1_1_0/deps/Pipeline-6.0.1-unix.tar.bz2
	mkdir loni
	tar -xvf Pipeline-6.0.1-unix.tar.bz2 -C loni

	#Get demo workflow
	cd $m2g/src/m2g/library/workflows/
	wget http://openconnecto.me/data/public/MR/m2g_v1_1_0/deps/m2g_test.pipe

	mkdir $HOME/.pipeline
	cd $HOME/.pipeline
	wget http://openconnecto.me/data/public/MR/m2g_v1_1_0/deps/preferences.xml

Export Paths and Setup Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

	echo "export m2g=/mrimages
	export M2G_HOME=${m2g}/src/m2g
	# Path to FSL
	FSLDIR=${m2g}/src/fsl
	. ${FSLDIR}/etc/fslconf/fsl.sh
	PATH=${FSLDIR}/bin:${PATH}
	export FSLDIR PATH

	# JAVA
	export PATH=${m2g}/src/java/jdk1.7.0_71/bin:$PATH
	export JAVA_HOME=${m2g}/src/java/jdk1.7.0_71

	#M2G
	export PATH='/usr/local/bin':${PATH}:${m2g}/src/m2g/MR-OCP/mrcap
	export PATH=${PATH}:${m2g}/src/m2g/packages/*
	export PYTHONPATH=${m2g}/src/m2g/MR-OCP
	export PYTHONPATH=${PYTHONPATH}:${m2g}/src/m2g/MR-OCP/MROCPdjango:${M2G_HOME}/MR-OCP/mrcap:${M2G_HOME}

	# Camino
	export PATH=${m2g}/src/camino/bin:$PATH
	export CAMINO_HEAP_SIZE=4000" > $m2g/.bashrc
	. $m2g/.bashrc

Running test workflow
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

	cd ${m2g}/src/loni
	./PipelineCLI.sh --validate ${m2g}/src/m2g/library/workflows/m2g_test.pipe
	./PipelineCLI.sh --execute ${m2g}/src/m2g/library/workflows/m2g_test.pipe

