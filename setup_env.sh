#!/bin/bash

# make sure that pwd is this repo root.
# TODO: convert to local venv within project
# TODO: separete a develop and require file?
conda create -n data-centric python=3.8 jupyterlab -y
conda activate data-centric
conda install keras -y
conda install -c conda-forge pre-commit nb_black flake8 isort pandas -y
pip install --editable .

pre-commit install
