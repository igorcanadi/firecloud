#!/bin/sh
source config.sh


for i in ${servers[@]}; do
    t=`date --rfc-3339=ns`
    ssh -i keys/id_rsa user739@$i "sudo date -s '$t'"
done
