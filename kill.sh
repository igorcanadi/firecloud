#!/bin/sh
source config.sh

if [ $# -eq 0 ]; then
    # no input, kill all of them
    who_to_kill=(0 1 2 3)
else 
    who_to_kill=($1)
fi

for i in ${who_to_kill[@]}; do
    echo "Killing " ${servers[$i]}
    ssh -i keys/id_rsa user739@${servers[$i]} "kill \`lsof | grep ${port} | awk '{print \$2}'\` 2> /dev/null"
done
