#!/bin/bash

# APT dependencies

DEP=`cat ../source/requirements-apt.txt`
sudo apt-get -y install $DEP

# PYTHON dependencies
sudo pip install -r ../source/requirements.txt
