#!/bin/bash
echo "Running script"

# Start server in macOS
service1="cd /Users/alex/Iris/chainlink && ./chainlink node start -p .password -a .api"
service2="cd /Users/alex/Iris/iris-external-adapter && conda activate sift && python app.py"

osascript -e "tell application \"Terminal\" to do script \"${service1}\""
osascript -e "tell application \"Terminal\" to do script \"${service2}\""

# Start server in Linux

# osascript -e 'tell application "Terminal" to activate' \
#     -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' \
#     -e 'tell application "Terminal" to do script "echo hello" in selected tab of the front window'
# osascript -e "
#       tell application \"Terminal\"
#         activate
#         tell application \"System Events\" to keystroke \"t\" using command down
#         repeat while contents of selected tab of window 1 starts with linefeed
#           delay 0.01
#         end repeat
#         do script \"${service1}\" in window 1
#       end tell
#     "
#./chainlink node start && python /iris-external-adapter app.py