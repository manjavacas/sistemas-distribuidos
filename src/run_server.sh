#!/bin/bash

rm -f -r ./*.log ./db/registry ./__pycache__ ./IceStorm
mkdir -p ./db/registry IceStorm/
touch downloader.log orchestrator.log

CONFIG_REGISTRY=node.config
CONFIG_ICEBOX=icebox.config
CONFIG_DOWNLOADER=downloader.config
CONFIG_ORCHESTRATOR=orchestrator.config

icegridregistry --Ice.Config=$CONFIG_REGISTRY &
icebox --Ice.Config=$CONFIG_ICEBOX &

./downloader.py --Ice.Config=$CONFIG_DOWNLOADER > downloader.log &
PID=$!

sleep 1
./orchestrator.py "$(head -1 downloader.log)" --Ice.Config=$CONFIG_ORCHESTRATOR > orchestrator.log

echo "Shutting down..."
kill -KILL $PID
