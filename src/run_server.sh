#!/bin/bash

rm -f -r ./*.proxy /tmp/db/registry
mkdir -p /tmp/db/registry

icegridregistry --Ice.Config=Node.config & 

./downloader.py --Ice.Config=Downloader.config & 

sleep 1
./orchestrator.py "$(head -1 downloader.proxy)" --Ice.Config=Orchestrator.config
