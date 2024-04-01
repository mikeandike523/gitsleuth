#!/bin/bash

# install.sh

cd /usr/local/src

# in case a previous isntallation was present
sudo rm -rf gitsleuth

sudo git clone https://www.github.com/mikeandike523/gitsleuth

cd gitsleuth

sudo chmod +x ./configure

sudo ./configure