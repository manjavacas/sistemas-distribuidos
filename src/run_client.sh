#!/bin/bash

url="https://www.youtube.com/watch?v=W1b1laUX_hc"

./client.py "$(cat orchestrator.proxy)" $url --Ice.Config=Client.config
