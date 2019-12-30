#!/bin/bash

rm -f -r ./db/registry ./IceStorm
mkdir -p ./db/registry IceStorm/

CONFIG_REGISTRY=node.config
CONFIG_ICEBOX=icebox.config

icegridregistry --Ice.Config=$CONFIG_REGISTRY &
icebox --Ice.Config=$CONFIG_ICEBOX

echo "Shutting down..."