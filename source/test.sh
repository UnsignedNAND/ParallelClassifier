#!/usr/bin/env bash
source openrc

mkdir times
timestamp=$(date +%s)

sed "s/level.*/level = info/" wiki.conf > wiki.conf.bak
        mv wiki.conf.bak wiki.conf

for PROCESSES in 1 2 3 4 5 6 7 8
do
    for ITEM_LIMIT in 10
    do
        sed "s/item_limit.*/item_limit = $ITEM_LIMIT/" wiki.conf > wiki.conf.bak
        mv wiki.conf.bak wiki.conf

        sed "s/processes.*/processes = $PROCESSES/" wiki.conf > wiki.conf.bak
        mv wiki.conf.bak wiki.conf

        bash run.sh | grep TIME_FOR >> times/${timestamp}.txt
    done
done
