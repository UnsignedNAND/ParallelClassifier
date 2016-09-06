#!/usr/bin/env bash
source openrc

python pwc.py \
    --debug \
    --parse \
    --distance \
    --cluster \
    --classify \
    --svm
