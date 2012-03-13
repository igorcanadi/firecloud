#!/bin/sh
source config.sh

if [ $# -lt 3 ]; then
    echo "usage: ./partition.sh {-A|-D} server1 server2"
    echo "-A for creating partitions"
    echo "-D for healing partitions"
    echo "server can be 0, 1, 2, or 3"
    exit
fi

ssh -i keys/id_rsa -p ${ports[$2]} user739@localhost "sudo iptables $1 INPUT -s ${servers[$3]} -j REJECT 2> /dev/null"
ssh -i keys/id_rsa -p ${ports[$3]} user739@localhost "sudo iptables $1 INPUT -s ${servers[$2]} -j REJECT 2> /dev/null"
