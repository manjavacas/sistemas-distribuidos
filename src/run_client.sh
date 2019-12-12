#!/bin/bash

CONFIG_CLIENT=client.config

./client.py "$(head -1 orchestrator.log)" $1 --Ice.Config=$CONFIG_CLIENT