#!/bin/bash

for sid in $(screen -ls | grep 'neo-cli' | awk '{print $1}'); do echo $sid; done
for sid in $(screen -ls | grep 'neo-cli' | awk '{print $1}'); do screen -S $sid -X quit; done