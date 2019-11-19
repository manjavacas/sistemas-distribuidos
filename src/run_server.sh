#!/bin/bash

rm -f -r ./*.out /tmp/db/registry
mkdir -p /tmp/db/registry

icegridregistry --Ice.Config=Node.config & 

./downloader.py --Ice.Config=Downloader.config > downloader.out & 

sleep 1
./orchestrator.py "$(head -1 downloader.out)" --Ice.Config=Orchestrator.config > orchestrator.out