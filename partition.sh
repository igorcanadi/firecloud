#!/bin/sh

if [ $# -lt 3 ]; then
    echo "usage: ./partition.sh {-A|-D} server1 server2"
    echo "-A for creating partitions"
    echo "-D for healing partitions"
    exit
fi

ssh -i keys/id_rsa user739@$2 "sudo iptables $1 INPUT -s $3 -j REJECT 2> /dev/null"
ssh -i keys/id_rsa user739@$3 "sudo iptables $1 INPUT -s $2 -j REJECT 2> /dev/null"
