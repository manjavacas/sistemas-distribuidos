#!/bin/bash

touch downloader.log transfer.log orchestrator.log

CONFIG_DOWNLOADER_FACTORY=downloader.config
CONFIG_TRANSFER_FACTORY=transfer.config
CONFIG_ORCHESTRATOR=orchestrator.config

./downloader_factory.py --Ice.Config=$CONFIG_DOWNLOADER_FACTORY > downloader.log &
PID1=$!

./transfer_factory.py --Ice.Config=$CONFIG_TRANSFER_FACTORY > transfer.log &
PID2=$!

sleep 1
./orchestrator.py "$(head -1 downloader.log)" "$(head -1 transfer.log)" --Ice.Config=$CONFIG_ORCHESTRATOR > orchestrator.log

echo "Shutting down..."
kill -KILL $PID1 $PID2
