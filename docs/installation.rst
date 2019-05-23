============
Installation
============

There are two general options to install and run NiBetaSeries: either in its containerized version (Docker or Singularity) or
manually prepared environment (Python 3.6+).

Containerized version
---------------------

Running the containerized version of NiBetaSeries, requires the installation of the respective
software, that is either `Docker <https://docs.docker.com/install/>`_ or `Singularity <https://www.sylabs.io/guides/3.0/user-guide/installation.html>`_.
Once installed, get either the NiBetaSeries docker image via:

::

  docker pull hbclab/nibetaseries:<version>

or the NiBetaSeries singularity image via:

::

  singularity build /path/to/image/nibetaseries-<version>.simg docker://HBClab/nibetaseries:<version>

Note: both should be run in the command line and *version* be replaced with the specific version of NiBetaSeries you want to run.

Once the image is completely pulled, the containerized version of NiBetaSeries is evoked from the command line as indicated hereinafter:

*Docker*:

::

  docker run -it --rm -v /path/to/bids_dir:/bids_dir \
                       -v /path/to/output_dir:/out_dir  \
                       -v /path/to/work_dir:/work_dir \
                       HBClab/nibetaseries:<version> \
                       nibs -c WhiteMatter CSF \
                             --participant_label 001 \
                             -w {work_dir} \
                             -a {atlas_mni_file} \
                             -l {atlas_tsv} \
                             {bids_dir} \
                             fmriprep \
                             {out_dir} \
                             participant

*Singularity*:

::

  singularity run --cleanenv -B /path/to/bids_dir:/bids_dir \
                              -B /path/to/output_dir:/out_dir  \
                              -B /path/to/work_dir:/work_dir \
                              path/to/image/nibetaseries-<version>.simg \
                              nibs -c WhiteMatter CSF \
                                    --participant_label 001 \
                                    -w {work_dir} \
                                    -a {atlas_mni_file} \
                                    -l {atlas_tsv} \
                                    {bids_dir} \
                                    fmriprep \
                                    {out_dir} \
                                    participant

Note: the Singularity example depicted above assumes that Singularity is configured in such a way
that folders on your host are not automatically bound (mounted or exposed). In case they are, the
*-B* lines can be neglected and paths on your host should be indicated regarding *-w*, *bids_dir* and *out_dir*.


Manually prepared environment (Python 3.6+)
-------------------------------------------

In order to install the NiBetaSeries python module type the following in the command line:

::

    pip install nibetaseries

Afterwards, NiBetaSeries can be run as follows from the command line:

::

  nibs -c WhiteMatter CSF \
        --participant_label 001 \
        -w {work_dir} \
        -a {atlas_mni_file} \
        -l {atlas_tsv} \
        {bids_dir} \
        fmriprep \
        {out_dir} \
        participant
