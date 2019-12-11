#!/bin/bash

CONFIG_CLIENT=client.config

if (( $# == 1 )); then
    ./client.py "$(head -1 orchestrator.log)" $1 --Ice.Config=$CONFIG_CLIENT
elif (( $# == 0 )); then
    ./client.py "$(head -1 orchestrator.log)" --Ice.Config=$CONFIG_CLIENT
else
    echo '[CLIENT] Usage: client.py <orchestrator_proxy> (<video_url>) --Ice.Config=client.config'
fi
