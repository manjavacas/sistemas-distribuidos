#!/bin/sh
#

echo "Downloading audio..."
./client.py orchestrator --download <url> \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py orchestrator --Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py orchestrator --transfer <file_name> \
--Ice.Config=client.config