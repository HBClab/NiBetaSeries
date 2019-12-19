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
    --run """\
curl -o pandoc-2.2.2.1-1-amd64.deb -sSL 'https://github.com/jgm/pandoc/releases/download/2.2.2.1/pandoc-2.2.2.1-1-amd64.deb' && \
dpkg -i pandoc-2.2.2.1-1-amd64.deb && \
rm pandoc-2.2.2.1-1-amd64.deb""" \
    --run 'chown -R neuro:users /src/nibetaseries' \
    --user=neuro \
    --workdir /src/nibetaseries \
    --run 'pip install --no-cache-dir .' \
    --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
    --workdir /home/neuro

}

generate_docker > Dockerfile

docker build -t hbclab/nibetaseries:dev .
# singularity build hbclab_nibetaseries.simg Singularity
