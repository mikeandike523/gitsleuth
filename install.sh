#!/bin/bash

# install.sh

# A convenience script to retrieve the latest version of this project install and configure it
# Typically called by
# curl https://github.com/mikeandike523/gitsleuth/blob/main/install.sh | bash

cd /usr/local/src

# in case a previous isntallation was present
sudo rm -rf gitsleuth

sudo git clone https://www.github.com/mikeandike523/gitsleuth

cd gitsleuth

sudo chmod +x ./configure

sudo ./configure