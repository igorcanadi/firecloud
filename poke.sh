#!/bin/sh
source config.sh

if [ $# -eq 1 ]; then
    # no input, kill all of them
    who_to_kill=(0 1 2 3)
    act=$1
else 
    who_to_kill=($1)
    act=$2
fi

for i in ${who_to_kill[@]}; do
    echo "Doing: " $act
    ssh -i keys/id_rsa user739@${servers[$i]} "$act"
done
