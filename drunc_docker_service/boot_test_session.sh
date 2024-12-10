#!/bin/bash

# setup dunedaq environment
. /basedir/NFD_DEV_241114_A9/env.sh

# boot full test session
if [[ "$CSC_SESSION" == "lr-session" ]]; then
    CONFIG="config/lrSession.data.xml"
    SESSION=$CSC_SESSION
else
    CONFIG="config/daqsystemtest/example-configs.data.xml"
    SESSION="local-1x1-config"
fi

drunc-process-manager-shell grpc://localhost:10054 boot $CONFIG $SESSION
