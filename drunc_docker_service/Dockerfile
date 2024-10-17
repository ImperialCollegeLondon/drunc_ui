FROM ghcr.io/dune-daq/frozen-release-alma9:fddaq-v5.1.0-a9

RUN yum install -y openssh-server && yum clean all

# required for dunedaq setup
SHELL ["/bin/bash", "-c"]

WORKDIR /basedir

# setup for the the dune development environment that provides the full set of
# dependencies required for booting of the controller test session
# See https://github.com/DUNE-DAQ/drunc/wiki/Setup-drunc-with-DUNE-DAQ for explanation
RUN source /cvmfs/dunedaq.opensciencegrid.org/setup_dunedaq.sh && \
        setup_dbt latest_v5 && \
        dbt-create fddaq-v5.1.0-a9 fddaq-v5.1.0-a9 && \
        cd fddaq-v5.1.0-a9 && \
        source env.sh && \
        dbt-build && \
        dbt-workarea-env && \
        pip install git+https://github.com/DUNE-DAQ/drunc.git@v0.10.2
WORKDIR /basedir/fddaq-v5.1.0-a9/

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
