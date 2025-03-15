# this makes an inpure shell env where we can run python commands like we would on a normal FHS OS
# so we can import the requirements.txt and the packages should install 


with import <nixpkgs> { };

let
  pythonPackages = python3Packages;

  startPythonScript = ''
    # put the commands to start python script here
    python main.py
  '';

  cleanupVenvScript = '' 
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
  '';
in pkgs.mkShell rec {
  name = "impurePythonEnv";
  venvDir = "./.venv";
  buildInputs = [
    # A Python interpreter including the 'venv' module is required to bootstrap
    # the environment.
    pythonPackages.python

    # This executes some shell code to initialize a venv in $venvDir before
    # dropping into the shell
    pythonPackages.venvShellHook

    # Those are dependencies that we would like to use from nixpkgs, which will
    # add them to PYTHONPATH and thus make them accessible from within the venv.
    pythonPackages.numpy
    pythonPackages.requests


    # In this particular example, in order to compile any binary extensions they may
    # require, the Python modules listed in the hypothetical requirements.txt need
    # the following packages to be installed locally:
    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    zlib

    stdenv.cc.cc.lib # needed this to import yfinance; it was giving me issues about not finding cstdlib++
    # ImportError: libstdc++.so.6: cannot open shared object file: No such file or directory
  ];

  preShellHook = ''
     ${cleanupVenvScript}
  '';
  
  # Run this command, only after creating the virtual environment
  postVenvCreation = ''
    unset SOURCE_DATE_EPOCH
    export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH # see default.nix
    
    # install after cleanup
    pip install -r requirements.txt
  '';

  # Now we can execute any commands within the virtual environment.
  postShellHook = ''
    # allow pip to install wheels
    unset SOURCE_DATE_EPOCH
    export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH # see default.nix
  '';
}


