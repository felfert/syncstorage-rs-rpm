#!/bin/bash

if [ $# -ge 1 -a -x $1 ] ; then
    CMD=$1
    shift
    exec $CMD "$@"
fi
if [ -n "$SYNC_CONFIG" ] ; then
    if [ -r "$SYNC_CONFIG" ] ; then
        exec /app/syncserver --config "$SYNC_CONFIG"
    else
        echo "Unable to read \"$SYNC_CONFIG\" forgot to mount VOLUME?"
        exit 1
    fi
fi
exec /app/syncserver
