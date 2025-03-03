#!/usr/bin/bash

if command -v drunc-session-manager
then
    /usr/sbin/sshd && drunc-session-manager
else
    while true
    do
        echo "drunc-session-manager not found -- run install_local_deps and restart"
        sleep 10
    done
fi
