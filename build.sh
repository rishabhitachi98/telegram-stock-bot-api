#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting TA-Lib Build Process..."

# Step 1: TA-Lib C++ library ko download aur compile karein
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz

# Compile aur project ke andar hi install karein
(cd ta-lib && ./configure --prefix=$PWD/../ta-lib-bin && make && make install)

echo "TA-Lib C++ library locally installed successfully."

# Step 2: Pip ko batayein ki TA-Lib kahan rakhi hai (Compile karne ke liye)
export TA_INCLUDE_PATH=$PWD/ta-lib-bin/include

# Step 3: --- YEH NAYI AUR ZAROORI LINE HAI ---
# Linker ko batayein ki TA-Lib kahan rakhi hai (Link karne ke liye)
export LD_LIBRARY_PATH=$PWD/ta-lib-bin/lib:$LD_LIBRARY_PATH

# Step 4: Ab Python dependencies install karein
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Build process finished successfully!"