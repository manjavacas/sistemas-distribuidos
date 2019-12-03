#!/bin/bash

# sample url: https://www.youtube.com/watch?v=AFkQ0By8N1g

if (( $# == 1 )); then
    ./client.py "$(head -1 orchestrator.out)" $1 --Ice.Config=Client.config
elif (( $# == 0 )); then
    ./client.py "$(head -1 orchestrator.out)" --Ice.Config=Client.config
else
    echo '[CLIENT] usage: client.py <orchestrator_proxy> (<file_url>) --Ice.Config=Client.config'
fi