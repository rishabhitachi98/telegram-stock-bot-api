#!/usr/bin/env bash
# exit on error
set -o errexit

# Isse build process saaf dikhega
echo "Starting TA-Lib Build Process..."

# Step 1: TA-Lib C++ library ko download aur compile karein
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz

# --- YEH LINE BADLI GAYI HAI ---
# Hum TA-Lib ko project ke andar hi ek 'ta-lib-bin' folder mein install karenge
(cd ta-lib && ./configure --prefix=$PWD/../ta-lib-bin && make && make install)

echo "TA-Lib C++ library locally installed successfully."

# Step 2: Pip ko batayein ki TA-Lib kahan rakhi hai
# Hum environment variable ka istemaal karenge
export TA_LIBRARY_PATH=$PWD/ta-lib-bin/lib
export TA_INCLUDE_PATH=$PWD/ta-lib-bin/include

# Step 3: Ab Python dependencies install karein
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Build process finished successfully!"