#!/bin/bash

# Setup python
source ./env/bin/activate
pip install -r ./requirements.txt
pip install -r ./piles_py/requirements.txt
pip install -r ./piles_static/requirements.txt

# Setup node.js
source ./piles_js/bootstrap.sh