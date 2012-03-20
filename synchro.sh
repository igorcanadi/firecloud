#!/bin/sh
source config.sh

t=`date --rfc-3339=ns`
echo $t

for i in ${servers[@]}; do
    ssh -i keys/id_rsa user739@$i "sudo date -s '$t'"
done
