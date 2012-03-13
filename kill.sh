#!/bin/sh
source config.sh

for i in 0 1 2 3; do
    echo "Killing " ${servers[$i]}
    ssh -i keys/id_rsa user739@localhost -p ${ports[$i]} "kill \`lsof | grep ${port} | awk '{print \$2}'\`"
done
