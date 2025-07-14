#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting TA-Lib Build Process..."

# Step 1: TA-Lib C++ library ko download aur compile karein
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz

# Compile aur locally install karein
(cd ta-lib && ./configure --prefix=/opt/render/project/src/ta-lib-bin && make && make install)

echo "TA-Lib C++ library locally installed successfully."

# Step 2: --- YEH SABSE ZAROORI LINE HAI ---
# Linker ko batayein ki hamari nayi library kahan rakhi hai
export LD_LIBRARY_PATH=/opt/render/project/src/ta-lib-bin/lib:$LD_LIBRARY_PATH

# Step 3: Ab Python dependencies install karein
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Build process finished successfully!"