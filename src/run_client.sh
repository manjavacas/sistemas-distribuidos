#!/bin/sh
#

echo "Downloading audio..."
./client.py orchestrator --download "https://www.youtube.com/watch?v=SSbBvKaM6sk" \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py orchestrator \
--Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py orchestrator --transfer "Blur - Song 2.mp3" \
--Ice.Config=client.config
