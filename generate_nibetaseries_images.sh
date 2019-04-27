#!/bin/sh

set -e

# Generate Dockerfile.
generate_docker() {
  docker run --rm kaczmarj/neurodocker:master generate docker \
    --base=neurodebian:stretch-non-free \
    --install gcc g++ \
    --pkg-manager=apt \
    --user=neuro \
    --miniconda \
      conda_install="python=3.6" \
      pip_install="jupyter seaborn" \
      create_env="neuro_py36" \
      activate=true \
    --copy requirements.txt /src/ \
    --copy . /src/nibetaseries \
    --workdir /src/ \
    --user=root \
    --run 'chmod -R 777 requirements.txt && chmod -R 777 /src/nibetaseries/' \
    --user=neuro \
    --run 'pip install --user --no-cache-dir -r requirements.txt' \
    --run 'cd /src/nibetaseries && pip install --no-cache-dir .[all]' \
    --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
    --workdir /home

}

# Generate Singularity recipe (does not include last --cmd arg)
generate_singularity() {
  docker run --rm kaczmarj/neurodocker:master generate singularity \
  --base=neurodebian:stretch-non-free \
  --install gcc g++ \
  --pkg-manager=apt \
  --user=neuro \
  --miniconda \
    conda_install="python=3.6" \
    pip_install="jupyter seaborn" \
    create_env="neuro_py36" \
    activate=true \
  --copy requirements.txt /src/ \
  --copy . /src/nibetaseries \
  --workdir /src/ \
  --user=root \
  --run 'chmod -R 777 requirements.txt && chmod -R 777 /src/nibetaseries/' \
  --user=neuro \
  --run 'pip install --user --no-cache-dir -r requirements.txt' \
  --run 'cd /src/nibetaseries && pip install --no-cache-dir .[all]' \
  --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \
  --workdir /home

}

generate_docker > Dockerfile
#generate_singularity > Singularity

docker build -t nibetaseries .
#singularity build nibetaseries.simg Singularity
