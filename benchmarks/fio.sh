#!/usr/bin/env bash

 fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=randrw --filename=test.fio --bs=4k --iodepth=64 --size=1G --readwrite=randrw --rwmixread=75
 rm test.fio
