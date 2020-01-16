#!/bin/sh
#

FILE_URL="https://www.youtube.com/watch?v=SSbBvKaM6sk"
FILE_NAME="Blur - Song 2.mp3"

echo "Downloading audio..."
./client.py orchestrator --download "$FILE_URL" \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py orchestrator \
--Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py orchestrator --transfer "$FILE_NAME" \
--Ice.Config=client.config
