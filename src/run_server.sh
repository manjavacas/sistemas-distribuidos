#!/bin/bash

mkdir -p /tmp/db/registry
icegridregistry --Ice.Config=Node.config

./downloader.py --Ice.Config=Downloader.config > downloader.proxy
./orchestrator.py "$(cat downloader.proxy)" --Ice.Config=Orchestrator.config > orchestrator.proxy
