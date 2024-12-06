FROM ghcr.io/imperialcollegelondon/dunedaq_dev_environment:nightly-241206

RUN yum install -y openssh-server && yum clean all

# required for dunedaq setup
SHELL ["/bin/bash", "-c"]

WORKDIR /basedir
ENV NIGHTLY_TAG=NFD_DEV_241206_A9

# setup for the the dune development environment that provides the full set of
# dependencies required for booting of the controller test session
# See https://github.com/DUNE-DAQ/drunc/wiki/Setup-drunc-with-DUNE-DAQ for explanation
ENV SPACK_ROOT /cvmfs/dunedaq-development.opensciencegrid.org/nightly/$NIGHTLY_TAG/spack-0.22.0
RUN source /cvmfs/dunedaq.opensciencegrid.org/setup_dunedaq.sh && \
    setup_dbt latest_v5 && \
    dbt-create -n "$NIGHTLY_TAG" && \
    cd "$NIGHTLY_TAG" && \
    source env.sh && \
    dbt-build && \
    dbt-workarea-env
WORKDIR /basedir/$NIGHTLY_TAG/

COPY process-manager-kafka.json /

# setup ssh server config and keys
ADD ssh-setup.sh /
RUN bash /ssh-setup.sh

RUN mkdir -p /usr/src/app
ADD entrypoint.sh /
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

ADD wibeth_output_all_zeros.bin /cvmfs/dunedaq.opensciencegrid.org/assets/files/d/d/1/wibeth_output_all_zeros.bin

ADD boot_test_session.sh /
RUN chmod a+x /boot_test_session.sh
