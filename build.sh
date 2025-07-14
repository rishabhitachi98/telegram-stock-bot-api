#!/usr/bin/env bash
# exit on error
set -o errexit

# TA-Lib ko download aur install karein
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
make install
cd ..

# Ab Python dependencies ko install karein
pip install -r requirements.txt