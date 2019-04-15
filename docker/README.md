# NiBetaSeries - docker & singularity

In order to ease up its application and reproducibility, both a NiBetaSeries [docker](https://www.docker.com/) and [singularity](https://www.sylabs.io/singularity/) image exist. The respective files are generated through [neurodocker](https://github.com/kaczmarj/neurodocker), with their build being automatized and checked using [circleci](https://circleci.com/).

To rebuild the images locally:

1. install [docker](https://docs.docker.com/install/) and/or [singularity](https://www.sylabs.io/guides/3.0/user-guide/installation.html) on your system

2. get the [neurodocker docker image](https://hub.docker.com/r/kaczmarj/neurodocker) from [docker hub](https://hub.docker.com/r/kaczmarj/neurodocker) </br>
</br>
`docker pull kaczmarj/neurodocker:master`

3. run the [generate_nibetaseries_images.sh]() script </br>
</br>
`bash generate_nibetaseries_images.sh`
