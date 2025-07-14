#!/usr/bin/env bash
# exit on error
set -o errexit

# Step 1: Install system dependencies for TA-Lib
apt-get update && apt-get install -y build-essential libta-lib-dev

# Step 2: Install Python dependencies
pip install -r requirements.txt