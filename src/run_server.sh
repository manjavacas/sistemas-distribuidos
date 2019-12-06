#!/bin/bash

rm -f -r ./*.out ./db/registry ./__pycache__ ./IceStorm
mkdir -p ./db/registry IceStorm/

touch downloader.out orchestrator.out

icegridregistry --Ice.Config=Node.config &
icebox --Ice.Config=icebox.config &

./downloader.py --Ice.Config=Downloader.config > downloader.out &

sleep 1
./orchestrator.py "$(head -1 downloader.out)" --Ice.Config=Orchestrator.config > orchestrator.out
