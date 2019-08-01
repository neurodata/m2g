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
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.6 python3.6-dev && \
    curl https://bootstrap.pypa.io/get-pip.py | python3.6

RUN pip3 install --upgrade pip

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

#--------NDMG SETUP-----------------------------------------------------------#
# setup of python dependencies for ndmg itself, as well as file dependencies
RUN \
    pip3.6 install numpy

RUN \
    pip3.6 install networkx nibabel dipy scipy python-dateutil pandas boto3 awscli matplotlib nilearn sklearn pandas cython vtk pyvtk fury awscli requests scikit-image ipython duecredit

RUN \
    pip3.6 install plotly==1.12.9 pybids==0.6.4 setuptools>=40.0

WORKDIR /

RUN mkdir /data && \
    chmod -R 777 /data

RUN mkdir /outputs && \
    chmod -R 777 /outputs

RUN git clone -b remove-zindex $NDMG_URL /ndmg && \
    cd /ndmg && \
    python3.6 setup.py install

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