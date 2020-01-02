#!/bin/bash

# Usage: ./run_client.sh <URL> <FILENAME>

CONFIG_CLIENT=client.config

./client.py "$(head -1 orchestrator.log)" --download $1 --Ice.Config=$CONFIG_CLIENT
./client.py "$(head -1 orchestrator.log)"