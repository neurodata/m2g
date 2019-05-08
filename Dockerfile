FROM neurodata/fsl_1604:0.0.1
MAINTAINER Derek Pisner <dpisner@utexas.edu>

#--------Environment Variables-----------------------------------------------#
ENV NDMG_URL https://github.com/neurodata/ndmg.git
ENV NDMG_ATLASES https://github.com/neurodata/neuroparc.git
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

# Configure git-lfs
RUN apt-get install -y apt-transport-https debian-archive-keyring
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get update && \
    apt-get install -y git-lfs

#---------AFNI INSTALL--------------------------------------------------------#
# setup of AFNI, which provides robust modifications of many of neuroimaging
# algorithms
RUN apt-get update -qq && apt-get install -yq --no-install-recommends ed gsl-bin libglu1-mesa-dev libglib2.0-0 libglw1-mesa fsl-atlases \
    libgomp1 libjpeg62 libxm4 netpbm tcsh xfonts-base xvfb && \
    libs_path=/usr/lib/x86_64-linux-gnu && \
    if [ -f $libs_path/libgsl.so.19 ]; then \
           ln $libs_path/libgsl.so.19 $libs_path/libgsl.so.0; \
    fi

RUN mkdir -p /opt/afni && \
    curl -o afni.tar.gz -sSLO "$AFNI_URL" && \
    tar zxv -C /opt/afni --strip-components=1 -f afni.tar.gz && \
    rm -rf afni.tar.gz
ENV PATH=/opt/afni:$PATH

#--------ANTS SETUP-----------------------------------------------------------#
RUN wget -qO- "https://cmake.org/files/v3.12/cmake-3.12.1-Linux-x86_64.tar.gz" | \
  tar --strip-components=1 -xz -C /usr/local

ENV ANTS_VERSION=2.2.0
WORKDIR /tmp
RUN git clone git://github.com/stnava/ANTs.git ants \
    && cd ants \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j8 \
    && mkdir -p /opt/ants \
    && mv bin/* /opt/ants && mv ../Scripts/* /opt/ants \
    && cd .. \
    && rm -rf build

ENV ANTSPATH=/opt/ants/ \
    PATH=/opt/ants:$PATH
#--------NDMG SETUP-----------------------------------------------------------#
# setup of python dependencies for ndmg itself, as well as file dependencies
RUN \
    pip install setuptools numpy networkx nibabel dipy scipy python-dateutil pandas boto3 awscli matplotlib nilearn sklearn pandas cython vtk pyvtk fury awscli requests scikit-image ipython duecredit --upgrade

RUN \
    pip install plotly==1.12.9 pybids==0.6.4

WORKDIR /

# Delete buggy line in dipy
RUN sed -i -e '189d;190d' /usr/local/lib/python2.7/dist-packages/dipy/tracking/eudx.py

RUN mkdir /data && \
    chmod -R 777 /data

RUN mkdir /outputs && \
    chmod -R 777 /outputs

RUN git clone -b dev-dmri-fmri $NDMG_URL /ndmg && \
    cd /ndmg && \
    python setup.py install

RUN mkdir /ndmg_atlases

RUN \
    git lfs clone $NDMG_ATLASES && \
    mv /neuroparc/atlases /ndmg_atlases && \
    rm -rf /neuroparc && \
    rm -rf /ndmg_atlases/label/Human/DS* && \
    rm -rf /ndmg_atlases/label/Human/pp264* && \
    rm -rf /ndmg_atlases/label/Human/princeton* && \
    rm -rf /ndmg_atlases/label/Human/slab* && \
    rm -rf /ndmg_atlases/label/Human/hemispheric

RUN chmod -R 777 /ndmg_atlases

ENV MPLCONFIGDIR /tmp/matplotlib
ENV PYTHONWARNINGS ignore

# copy over the entrypoint script
#ADD ./.vimrc .vimrc
RUN ldconfig
RUN chmod -R 777 /usr/local/bin/ndmg_bids

# and add it as an entrypoint
ENTRYPOINT ["ndmg_bids"]
