#!/bin/sh
source config.sh

for i in ${servers[@]}; do
    scp -i keys/id_rsa -P 22 -r * user739@$i:~
done
