#!/usr/bin/env bash
source openrc

python pwc.py \
    --parse \
    --distance \
    --cluster \
    --classify \
    --svm
