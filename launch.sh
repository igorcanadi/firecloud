#!/bin/sh
source config.sh

master=1
for i in 0 1 2 3; do
    echo "Launching " ${servers[$i]}
    ssh -i keys/id_rsa -p ${ports[$i]} user739@localhost "python server/main.py $i $master ${servers[0]}:$port ${servers[1]}:$port ${servers[2]}:$port ${servers[3]}:$port" &
    master=0
done
