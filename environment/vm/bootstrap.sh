#!/bin/bash

# add sources
## docker
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list

apt-get -y update
apt-get -y upgrade
apt-get -y dist-upgrade

# install & configure development stuff
apt-get -y install \
                git \
                python-pip \
                python-dev \
                tmux \
                vim

# install docker & dependencies
apt-get -y install linux-image-extra-$(uname -r)
apt-get -y install docker-engine

# configure docker for non-root user
usermod -aG docker vagrant

# cleaning
apt-get -y autoremove
