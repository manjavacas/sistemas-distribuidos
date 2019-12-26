#!/usr/bin/make -f
# -*- mode:makefile -*-


all: clean \
	start

start:
	$(MAKE) run-icestorm
	echo "icestorm running..."
	sleep 1
	$(MAKE) run-server
	echo "server running..."

run-server:
	gnome-terminal -- bash -c \
	"./run_server.sh; bash"

run-icestorm:
	mkdir -p IceStorm/
	gnome-terminal -- bash -c \
	"./run_icestorm.sh; bash"

clean:
	$(RM) *.log *.mp3
	$(RM) -r __pycache__ IceStorm db
