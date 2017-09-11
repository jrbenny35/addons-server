#!/bin/bash
set -ex

wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz
gunzip -c geckodriver.tar.gz | tar xopf -
chmod +x geckodriver
mv geckodriver /bin
geckodriver --version
apt-get install python3-pip

pip3 install tox mozdownload mozinstall

mozdownload --version latest --type daily --destination firefox
mozinstall $(ls -t firefox/*tar.bz2)
export PATH=firefox/firefox:$PATH
