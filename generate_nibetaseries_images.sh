#!/bin/sh

set -e

# Generate Dockerfile.
generate_docker() {
  docker run --rm kaczmarj/neurodocker:0.5.0 generate docker \
    --base=neurodebian:stretch-non-free \
    --install gcc g++ graphviz \
    --pkg-manager=apt \
    --user=neuro \
    --workdir="/home/neuro" \
    --miniconda \
      conda_install="python=3.6" \
      pip_install="jupyter seaborn tox" \
      create_env="neuro_py36" \
      activate=true \
    --copy . /src/nibetaseries \
    --user=root \
    --run 'chown -R neuro:users /src/nibetaseries' \
    --user=neuro \
    --workdir /src/nibetaseries \
    --run '. activate neuro_py36 && pip install --no-cache-dir .[test,dev,doc,nb]' \
    --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
    --workdir /home/neuro

}

generate_docker > Dockerfile

docker build -t hbclab/nibetaseries:dev .
# singularity build hbclab_nibetaseries.simg Singularity
