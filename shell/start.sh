#!/usr/bin/expect -f
set timeout -1
set neoclipath [lindex $argv 0]
cd $neoclipath

spawn screen -S neo-cli ./neo-cli -r
sleep 5
expect "neo>"

send "\01"
send "d"
