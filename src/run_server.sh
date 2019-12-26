#!/bin/bash

touch downloader.log orchestrator.log

CONFIG_DOWNLOADER=downloader.config
CONFIG_ORCHESTRATOR=orchestrator.config

./downloader.py --Ice.Config=$CONFIG_DOWNLOADER > downloader.log &
PID=$!

sleep 1
./orchestrator.py "$(head -1 downloader.log)" --Ice.Config=$CONFIG_ORCHESTRATOR > orchestrator.log

echo "Shutting down..."
kill -KILL $PID
