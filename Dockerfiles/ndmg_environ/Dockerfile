FROM dit4c/dit4c-container-fsl
MAINTAINER Greg Kiar <gkiar@jhu.edu>
RUN apt-get update && apt-get install -y python-dev python-setuptools python-numpy python-scipy zlib1g-dev python-matplotlib python-nose fsl
RUN easy_install pip
RUN pip install cython numpy coveralls wget nibabel nilearn dipy sklearn networkx && pip install ndmg
ENV FSLDIR=/usr/share/fsl/5.0
ENV PATH=${FSLDIR}/bin:${PATH}
# ENTRYPOINT ["/bin/bash"]
ENTRYPOINT ["/bin/bash", "-c", ". ${FSLDIR}/etc/fslconf/fsl.sh && /bin/bash"]
