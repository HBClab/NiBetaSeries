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
      pip_install="ipython nipype==1.1.5 pybids==0.6.4 nibabel==2.3.0 nistats==0.0.1b
                   nilearn==0.4.2 pandas==0.24.0 numpy==1.14.5 duecredit==0.6.4
                   scikit-learn==0.19.2 jupyter seaborn nibetaseries" \
      create_env="neuro_py36" \
      activate=true \
     --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \

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
    pip_install="ipython nipype==1.1.5 pybids==0.6.4 nibabel==2.3.0 nistats==0.0.1b
                 nilearn==0.4.2 pandas==0.24.0 numpy==1.14.5 duecredit==0.6.4
                 scikit-learn==0.19.2 jupyter seaborn nibetaseries" \
    create_env="neuro_py36" \
    activate=true \
  --run 'mkdir -p ~/.jupyter && echo c.NotebookApp.ip = \"0.0.0.0\" > ~/.jupyter/jupyter_notebook_config.py' \

}

generate_docker > Dockerfile
generate_singularity > Singularity

docker build -t nibetaseries .
singularity build nibetaseries.simg Singularity
