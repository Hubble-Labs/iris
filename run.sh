#!/bin/bash
echo "Running script"

service1="cd /Users/alex/Iris/chainlink && ./chainlink node start"
service2="cd /Users/alex/Iris/iris-external-adapter && python app.py"

osascript -e "tell application \"Terminal\" to do script \"${service1}\""
osascript -e "tell application \"Terminal\" to do script \"${service2}\""

#./chainlink node start && python /iris-external-adapter app.py