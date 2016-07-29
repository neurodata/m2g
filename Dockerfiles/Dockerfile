FROM dit4c/dit4c-container-fsl
MAINTAINER Greg Kiar <gkiar@jhu.edu>
RUN apt-get update && apt-get install -y python-dev python-setuptools python-numpy python-scipy zlib1g-dev python-matplotlib python-nose fsl ia32-libs
RUN easy_install pip
RUN pip install cython numpy coveralls wget nibabel nilearn dipy sklearn networkx && pip install ndmg

# FSL
ENV FSLDIR=/usr/share/fsl/5.0
ENV PATH=${FSLDIR}/bin:${PATH}
ENV POSSUMDIR=$FSLDIR
ENV PATH=/usr/lib/fsl/5.0:$PATH
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV FSLMULTIFILEQUIT=TRUE
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLBROWSER=/etc/alternatives/x-www-browser
ENV FSLLOCKDIR=
ENV FSLMACHINELIST=
ENV FSLREMOTECALL=
ENV FSLCLUSTER_MAILOPTS="n"
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

#S3
RUN mkdir ${HOME}/.aws
RUN printf "[default]\nregion = us-east-1" > ${HOME}/.aws/config
ADD credentials.csv ${HOME}/credentials.csv
RUN printf "[default]\naws_access_key_id = `tail -n 1 ${HOME}/credentials.csv | cut -d',' -f2`\naws_secret_access_key = `tail -n 1 ${HOME}/credentials.csv | cut -d',' -f3`" > ${HOME}/.aws/credentials

ENTRYPOINT ["ndmg_bids"]
