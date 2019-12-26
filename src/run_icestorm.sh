#!/bin/bash

rm -f -r ./*.log ./db/registry ./__pycache__ ./IceStorm
mkdir -p ./db/registry IceStorm/

CONFIG_REGISTRY=node.config
CONFIG_ICEBOX=icebox.config

icegridregistry --Ice.Config=$CONFIG_REGISTRY &
icebox --Ice.Config=$CONFIG_ICEBOX

echo "Shutting down..."