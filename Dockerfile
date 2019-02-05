FROM neurodata/fsl_1604:0.0.1
MAINTAINER Derek Pisner <dpisner@utexas.edu>

#--------Environment Variables-----------------------------------------------#
ENV NDMG_URL https://github.com/neurodata/ndmg.git
ENV NDMG_ATLASES s3://mrneurodata/resources/ndmg_atlases.zip 
ENV AFNI_URL https://files.osf.io/v1/resources/fvuh8/providers/osfstorage/5a0dd9a7b83f69027512a12b
ENV LIBXP_URL http://mirrors.kernel.org/debian/pool/main/libx/libxp/libxp6_1.0.2-2_amd64.deb 
ENV LIBPNG_URL http://mirrors.kernel.org/debian/pool/main/libp/libpng/libpng12-0_1.2.49-1%2Bdeb7u2_amd64.deb

#--------Initial Configuration-----------------------------------------------#
# download/install basic dependencies, and set up python
RUN apt-get update && \
    apt-get install -y zip unzip vim git curl libglu1 python-setuptools zlib1g-dev \
    git libpng-dev libfreetype6-dev pkg-config g++ vim r-base-core libgsl0-dev build-essential \
    openssl

# upgrade python to solve TLS issues
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get update && \
    add-apt-repository ppa:jonathonf/python-2.7 && \
    apt-get update && \
    apt-get install -y python2.7 python2.7-dev

RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py

RUN pip install --upgrade pip

# Get neurodebian config
RUN curl -sSL http://neuro.debian.net/lists/stretch.us-tn.full >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key add /root/.neurodebian.gpg && \
    (apt-key adv --refresh-keys --keyserver hkp://ha.pool.sks-keyservers.net 0xA5D32F012649A5A9 || true) && \
    apt-get update -qq
RUN apt-get -f install

###################################################################################################################
# Download sources & setup supporting libraries that are needed to build VTK
# Else use pip install vtk pyvtk during later pypi installs
###################################################################################################################
# Create source & tmp build directory
RUN mkdir /tmpbuild
WORKDIR /tmpbuild

# Download & extract VTK
RUN wget http://www.vtk.org/files/release/7.0/VTK-7.0.0.tar.gz && tar -zxvf VTK-7.0.0.tar.gz

# Download, extract & build CMake
# http://www.vtk.org/Wiki/VTK/Configure_and_Build
RUN wget http://www.cmake.org/files/v2.8/cmake-2.8.12.2.tar.gz \
    && tar xzf cmake-2.8.12.2.tar.gz
RUN cd cmake-2.8.12.2 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install

# Install OpenGL
# Debian, Ubuntu
# https://en.wikibooks.org/wiki/OpenGL_Programming/Installation/Linux
RUN apt-get update && apt-get install --yes build-essential libgl1-mesa-dev

# Download & build Tcl
# https://www.tcl.tk/doc/howto/compile.html#unix
RUN wget http://prdownloads.sourceforge.net/tcl/tcl8.6.6-src.tar.gz && tar -zxvf tcl8.6.6-src.tar.gz
RUN cd tcl8.6.6/unix && ./configure && make && make install

# Download & build Tk
# https://www.tcl.tk/doc/howto/compile.html
RUN wget http://prdownloads.sourceforge.net/tcl/tk8.6.6-src.tar.gz && tar -zxvf tk8.6.6-src.tar.gz
RUN cd tk8.6.6/unix && ./configure && make && make install
###################################################################################################################
# /end setup
###################################################################################################################

###################################################################################################################
# Building VTK with python interfaces
# http://ghoshbishakh.github.io/blog/blogpost/2016/03/05/buid-vtk.html
###################################################################################################################
RUN mkdir /vtk-build2

RUN apt-get install -y libxt-dev

RUN cd /vtk-build2/ && cmake \
  -DCMAKE_BUILD_TYPE:STRING=Release \
  -DBUILD_TESTING:BOOL=OFF \
  -DVTK_WRAP_PYTHON:BOOL=ON \
  -DVTK_WRAP_PYTHON_SIP:BOOL=ON \
  -DVTK_WRAP_TCL:BOOL=ON \
  -DVTK_PYTHON_VERSION:STRING=3 \
  -DVTK_USE_TK:BOOL=ON \
  /tmpbuild/VTK-7.0.0

# Build VTK
RUN cd /vtk-build2/ && make

# Now install the python bindings
RUN cd /vtk-build2/Wrapping/Python && make && make install

# Set environment variable to add the VTK libs to the Shared Libraries
# http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/vtk-build2/lib
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/lib:/vtk-build2/lib
###################################################################################################################
# /end VTK Build
###################################################################################################################

#---------AFNI INSTALL--------------------------------------------------------#
# setup of AFNI, which provides robust modifications of many of neuroimaging
# algorithms
RUN apt-get update -qq && apt-get install -yq --no-install-recommends ed gsl-bin libglu1-mesa-dev libglib2.0-0 libglw1-mesa fsl-atlases \
    libgomp1 libjpeg62 libxm4 netpbm tcsh xfonts-base xvfb && \
    libs_path=/usr/lib/x86_64-linux-gnu && \
    if [ -f $libs_path/libgsl.so.19 ]; then \
           ln $libs_path/libgsl.so.19 $libs_path/libgsl.so.0; \
    fi

RUN echo "Install libxp (not in all ubuntu/debian repositories)" && \
    apt-get install -yq --no-install-recommends libxp6 \
    || /bin/bash -c " \
       curl --retry 5 -o /tmp/libxp6.deb -sSL \
       && dpkg -i /tmp/libxp6.deb && rm -f /tmp/libxp6.deb $LIBXP_URL" && \
    echo "Install libpng12 (not in all ubuntu/debian repositories" && \
    apt-get install -yq --no-install-recommends libpng12-0 \
    || /bin/bash -c " \
       curl -o /tmp/libpng12.deb -sSL $LIBPNG_URL \
       && dpkg -i /tmp/libpng12.deb && rm -f /tmp/libpng12.deb" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /opt/afni && \
    curl -o afni.tar.gz -sSLO "$AFNI_URL" && \
    tar zxv -C /opt/afni --strip-components=1 -f afni.tar.gz && \
    rm -rf afni.tar.gz
ENV PATH=/opt/afni:$PATH

#--------NDMG SETUP-----------------------------------------------------------#
# setup of python dependencies for ndmg itself, as well as file dependencies
RUN \
    pip install numpy networkx>=1.11 nibabel>=2.0 dipy==0.14.0 scipy \
    python-dateutil==2.6.1 boto3 awscli matplotlib==1.5.3 plotly==1.12.9 nilearn>=0.2 sklearn>=0.0 \
    pandas cython pyvtk awscli requests==2.5.3 scikit-image pybids==0.6.4 ipython

RUN \
    git clone -b dev-dmri-fmri $NDMG_URL /ndmg && \
    cd /ndmg && \
    python setup.py install 

RUN \
    mkdir /ndmg_atlases && \
    cd /ndmg_atlases && \
    aws s3 cp --no-sign-request $NDMG_ATLASES ./ && \
    unzip ndmg_atlases.zip

RUN mkdir /data && \
    chmod -R 777 /data

ENV MPLCONFIGDIR /tmp/matplotlib
ENV PYTHONWARNINGS ignore

# copy over the entrypoint script
#ADD ./.vimrc .vimrc
RUN ldconfig
RUN chmod -R 777 /usr/local/bin/ndmg_bids

# and add it as an entrypoint
ENTRYPOINT ["ndmg_bids"]
