#!/usr/bin/env bash
source openrc

rm wiki.log

python pwc.py \
    --debug \
    --parse \
    --distance \
    --cluster \
    --classify \
    --svm
