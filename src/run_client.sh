#!/bin/bash

url="https://www.youtube.com/watch?v=W1b1laUX_hc"

./client.py "$(head -1 orchestrator.proxy)" $url --Ice.Config=Client.config &
PID=$!

wait $PID
