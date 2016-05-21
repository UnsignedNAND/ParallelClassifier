#!/usr/bin/env bash

diskutil erasevolume HFS+ 'RAMDisk' `hdiutil attach -nomount ram://8388608`