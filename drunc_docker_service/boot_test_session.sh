#!/bin/bash

# setup dunedaq environment
. /basedir/fddaq-v5.1.0-a9/env.sh

# boot full test session
drunc-process-manager-shell grpc://localhost:10054 boot test/config/test-session.data.xml test-session
