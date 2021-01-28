#!/bin/bash

if ! ps ax | grep -q "[P]iEnvironmentMonitor.py"; then
    echo "Starting Environment Monitor ..."
    nohup python3 -u PiEnvironmentMonitor.py  > logs/monitor.log &
else
    echo "Environment Monitor already running!"
fi