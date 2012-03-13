#!/bin/sh
source config.sh

if [ $# -lt 2 ]; then
    # no input, start all of them
    who_to_start=(0 1 2 3)
    master=1
else 
    # usage: [index of the server] [is_master]
    who_to_start=($1)
    master=($2)
fi

for i in ${who_to_start[@]}; do
    echo "Launching " ${servers[$i]}
    ssh -i keys/id_rsa -p ${ports[$i]} user739@localhost "python server/main.py $i $master ${servers[0]}:$port ${servers[1]}:$port ${servers[2]}:$port ${servers[3]}:$port 2> /dev/null" &
    master=0
done
