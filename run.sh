#!/bin/sh

until ./pidar.py /dev/ttyACM0; do
	echo "Server exited with code $?.  Respawning..." >&2
	sleep 1
done
