#!/usr/bin/env bash
# exit on error
set -o errexit

# Isse build process saaf dikhega
echo "Starting build process..."

# Step 1: TA-Lib C++ library ko download aur compile karein
echo "Downloading and compiling TA-Lib C++ library..."
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz

# Folder ke andar jaakar compile karein
(cd ta-lib && ./configure --prefix=/usr && make && make install)

echo "TA-Lib C++ library installed successfully."

# Step 2: Ab Python dependencies install karein
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Build process finished successfully!"