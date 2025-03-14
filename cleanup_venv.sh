# Check if requirements.txt has changed by comparing hash
if [ ! -f "requirements-sha.txt" ] || \
   [ "$(sha256sum requirements.txt)" != "$(cat requirements-sha.txt 2>/dev/null)" ] || \
   [ ! -d ".venv" ]; then
    
    # Remove existing venv
    [ -d ".venv" ] && rm -rf .venv
    
    # Create new venv and install requirements
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Save new hash
    sha256sum requirements.txt > requirements-sha.txt
    
    echo "Virtual environment updated with new dependencies."
else
    echo "Requirements unchanged. Using existing virtual environment."
fi

