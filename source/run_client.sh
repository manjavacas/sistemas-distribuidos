#!/bin/bash

./client.py "$(cat orchestrator.proxy)" $1 --Ice.Config=Client.config
