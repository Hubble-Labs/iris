#!/bin/bash
echo "Running script"

service1="cd /Users/alex/Iris/chainlink && ./chainlink node start"

osascript -e "tell application \"Terminal\" to do script \"${service1}\""

#./chainlink node start && python /iris-external-adapter app.py