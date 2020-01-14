#!/bin/sh
#

echo "Downloading audio..."
./client.py "orchestrator2 -t -e 1.1 @ ReplicatedOrchestratorAdapter" --download "https://www.youtube.com/watch?v=SSbBvKaM6sk" \
--Ice.Config=client.config

echo ""
echo "List request..."
./client.py "orchestrator2 -t -e 1.1 @ ReplicatedOrchestratorAdapter" \
--Ice.Config=client.config

echo ""
echo "Init transfer..."
./client.py "orchestrator2 -t -e 1.1 @ ReplicatedOrchestratorAdapter" --transfer "Blur - Song 2.mp3" \
--Ice.Config=client.config
