#!/bin/sh
#

echo "Downloading audio..."
./client.py --download "https://www.youtube.com/watch?v=SSbBvKaM6sk" \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py --Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py --transfer <file_name> \
--Ice.Config=client.config