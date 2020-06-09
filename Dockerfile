FROM neurodata/fsl_1604:0.0.1
LABEL author="Ross Lawrence, Alex Loftus"
LABEL maintainer="rlawre18@jhu.edu"

#--------Environment Variables-----------------------------------------------#
ENV M2G_URL https://github.com/neurodata/m2g.git
ENV M2G_ATLASES https://github.com/neurodata/neuroparc.git
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

RUN apt-get install -y python2.7 python-pip

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

# #---------AFNI INSTALL--------------------------------------------------------#
# # setup of AFNI, which provides robust modifications of many of neuroimaging
# # algorithms
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

## --------CPAC INSTALLS-----------------------------------------------------#
RUN apt-get install -y graphviz graphviz-dev

# Setup FSL environment
ENV FSLDIR=/usr/share/fsl/5.0 \
    FSLOUTPUTTYPE=NIFTI_GZ \
    FSLMULTIFILEQUIT=TRUE \
    POSSUMDIR=/usr/share/fsl/5.0 \
    LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH \
    FSLTCLSH=/usr/bin/tclsh \
    FSLWISH=/usr/bin/wish \
    PATH=/usr/lib/fsl/5.0:$PATH

# install CPAC resources into FSL
RUN curl -sL http://fcon_1000.projects.nitrc.org/indi/cpac_resources.tar.gz -o /tmp/cpac_resources.tar.gz && \
    tar xfz /tmp/cpac_resources.tar.gz -C /tmp && \
    cp -n /tmp/cpac_image_resources/MNI_3mm/* $FSLDIR/data/standard && \
    cp -n /tmp/cpac_image_resources/MNI_4mm/* $FSLDIR/data/standard && \
    cp -n /tmp/cpac_image_resources/symmetric/* $FSLDIR/data/standard && \
    cp -n /tmp/cpac_image_resources/HarvardOxford-lateral-ventricles-thr25-2mm.nii.gz $FSLDIR/data/atlases/HarvardOxford && \
    cp -nr /tmp/cpac_image_resources/tissuepriors/2mm $FSLDIR/data/standard/tissuepriors && \
    cp -nr /tmp/cpac_image_resources/tissuepriors/3mm $FSLDIR/data/standard/tissueprior


#--------M2G SETUP-----------------------------------------------------------#
# setup of python dependencies for m2g itself, as well as file dependencies
RUN \
    pip3.6 install --no-cache-dir virtualenv numpy nibabel scipy python-dateutil pandas boto3 awscli
RUN \
    pip3.6 install --no-cache-dir matplotlib nilearn sklearn pandas cython vtk pyvtk fury
RUN \
    pip3.6 install --no-cache-dir awscli requests ipython duecredit graspy scikit-image networkx dipy pybids

RUN \
    pip3.6 install --no-cache-dir plotly==1.12.9 setuptools>=40.0 configparser>=3.7.4

WORKDIR /

RUN mkdir /input && \
    chmod -R 777 /input

RUN mkdir /output && \
    chmod -R 777 /output

# grab atlases from neuroparc
RUN mkdir /m2g_atlases

RUN \
    git lfs clone https://github.com/neurodata/neuroparc -b paper-fixes && \
    mv /neuroparc/atlases /m2g_atlases && \
    rm -rf /neuroparc
RUN chmod -R 777 /m2g_atlases

# Grab m2g from deploy.
RUN git clone -b Priebe-edits $M2G_URL /m2g && \
    cd /m2g && \
    pip3.6 install .
RUN chmod -R 777 /usr/local/bin/m2g_bids

ENV MPLCONFIGDIR /tmp/matplotlib
ENV PYTHONWARNINGS ignore

# copy over the entrypoint script
#ADD ./.vimrc .vimrc
RUN ldconfig

# and add it as an entrypoint
ENTRYPOINT ["m2g"]

# Clear apt-get caches (try adding sudo)
RUN apt-get clean

# Set up the functional pipeline
RUN cd / && \
    git clone https://github.com/FCP-INDI/C-PAC.git && \
    mkdir /code && \
    mv /C-PAC/dev/docker_data/* /code/ && \
    mv /C-PAC/* /code/ && \
    rm -R /C-PAC && \
    chmod +x /code/run.py && \
    cd /

# due to cpac's requirments.txt being out of order, nilearn is installed before scipy and scikit-learn (which it needs)
RUN virtualenv -p /usr/bin/python2.7 venv && \
    . venv/bin/activate && \
    pip install --upgrade pip==9.0.1 && \
    ls /code && \
    pip install scipy==1.2.1 --no-cache-dir && \
    pip install scikit-learn==0.19.1 --no-cache-dir && \
    pip install -r /code/requirements.txt --no-cache-dir && \
    pip install -e /code && \
    pip install torch==1.2.0 --no-cache-dir && \
    pip install torch==1.2.0 torchvision==0.4.0 -f https://download.pytorch.org/whl/torch_stable.html --no-cache-dir && \
    pip install xvfbwrapper