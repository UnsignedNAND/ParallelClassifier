#!/bin/bash

for var in "$@"
do
    rsync --recursive \
          --human-readable \
          --progress \
          --exclude '/.*/' \
          --exclude '/*backup*/' \
          --exclude '*.pyc' \
          --exclude '*.xml' \
          --exclude '*.bz2' \
          ../ \
          root@$var:~/msc/
done
