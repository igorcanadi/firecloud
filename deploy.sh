#!/bin/sh
source config.sh

for i in ${ports[@]}; do
    scp -i keys/id_rsa -P $i -r * user739@localhost:~
done
