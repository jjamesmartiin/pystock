# basic explanation:
- this is a nix project written in python for tracking stocks

# using:
## python dependencies
- make sure to add dependencies to the requirements.txt file and then remove the .venv folder
    - if we don't remove the venv folder then we will not download the new dependencies
    > is there a way to fix that? 
    > maybe we can check the sha256 of requirements.txt and write it to a file called requirements-sha.txt; if it's different or that file doesn't exist, then we should remove the .venv folder
- they will be installed with pip during the nix-shell
