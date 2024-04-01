#!/bin/bash

# install.sh

cd /usr/local/src

sudo rm -rf gitsleuth

sudo git clone https://www.github.com/mikeandike523/gitsleuth

cd gitsleuth

sudo chmod +x ./configure

sudo ./configure