#!/usr/bin/expect -f
set timeout -1

spawn screen -r neo-cli
sleep 2
expect "neo>"

send "exit\r"
expect eof