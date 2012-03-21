#!/bin/sh
source config.sh

if [ $# -lt 1 ]; then
    # no input, start all of them
    who_to_start=(0 1 2 3)
else 
    # usage: [index of the server]
    who_to_start=($1)
fi

for i in ${who_to_start[@]}; do
    echo "Launching " ${servers[$i]}
    ssh -i keys/id_rsa user739@${servers[$i]} "python server/main.py $i ${servers[0]}:$port ${servers[1]}:$port ${servers[2]}:$port ${servers[3]}:$port" &
done
