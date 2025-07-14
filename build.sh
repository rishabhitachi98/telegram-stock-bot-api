#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting TA-Lib Build Process..."

# Step 1: TA-Lib C++ library ko download aur compile karein
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz

# Compile aur project ke andar hi install karein
(cd ta-lib && ./configure --prefix=/opt/render/project/src/ta-lib-bin && make && make install)

echo "TA-Lib C++ library locally installed successfully."

# Step 2: --- YEH SABSE IMPORTANT HISSA HAI ---
# Hum pehle TA-Lib ko alag se install karenge, saare paths dekar
pip install --global-option=build_ext --global-option="-I/opt/render/project/src/ta-lib-bin/include" --global-option="-L/opt/render/project/src/ta-lib-bin/lib" TA-Lib

# Step 3: Ab baaki dependencies ko install karein
echo "Installing remaining Python dependencies..."
pip install -r requirements.txt

echo "Build process finished successfully!"