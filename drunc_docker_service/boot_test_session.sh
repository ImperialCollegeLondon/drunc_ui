#!/bin/bash

# boot full test session
if [[ "$CSC_SESSION" == "lr-session" ]]; then
    CONFIG="oksconflibs:config/lrSession.data.xml"
    SESSION=$CSC_SESSION
    SESSION_NAME=$CSC_SESSION
else
    CONFIG="oksconflibs:config/daqsystemtest/example-configs.data.xml"
    SESSION="local-1x1-config"
    SESSION_NAME="local-1x1-config"
fi

/entrypoint.sh drunc-process-manager-shell grpc://localhost:10054 boot $CONFIG $SESSION_NAME $SESSION
