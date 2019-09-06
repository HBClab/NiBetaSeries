.. _installation:

============
Installation
============

.. Note:: All code examples should be run in the command line.

There are two general options to install and run NiBetaSeries:
either in its containerized version (Docker or Singularity) or
manually prepared environment (Python 3.5+).

Docker Container
----------------

If you have administrative privileges on your workstation
(i.e., are able to install software on your system),
`Docker <https://docs.docker.com/install/>`_ is a great way to keep
everything in the code environment constant/reproducible
(not just the NiBetaSeries code).
Once you have docker, you can download the NiBetaSeries docker image via:

::

  docker pull hbclab/nibetaseries:vX.Y.Z

.. Note::

  *X.Y.Z* should replaced with the specific version of
  NiBetaSeries you want to run (e.g. 0.2.3).

Once the image is completely pulled, the containerized version of
NiBetaSeries is evoked from the command line:

::

  docker run -it --rm -v /path/to/bids_dir:/bids_dir \
                       -v /path/to/output_dir:/out_dir  \
                       -v /path/to/work_dir:/work_dir \
                       HBClab/nibetaseries:<version> \
                       nibs -c WhiteMatter CSF \
                             --participant-label 001 \
                             -w {work_dir} \
                             -a {atlas_mni_file} \
                             -l {atlas_tsv} \
                             {bids_dir} \
                             fmriprep \
                             {out_dir} \
                             participant

Singularity Container
---------------------

If you do not have administrative privileges and/or are using a cluster,
`Singularity <https://www.sylabs.io/guides/3.0/user-guide/installation.html>`_
is a good choice to get the same benefits as Docker.
You may have to ask your administrator to install Singularity.
Once Singularity is installed, you can pull the NiBetaSeries image via:

::

  singularity build /path/to/image/nibetaseries-vX.Y.Z.simg docker://HBClab/nibetaseries:vX.Y.Z

Once the image is completely pulled, the containerized version of
NiBetaSeries is evoked from the command line:

::

  singularity run --cleanenv -B /path/to/bids_dir:/bids_dir \
                              -B /path/to/output_dir:/out_dir  \
                              -B /path/to/work_dir:/work_dir \
                              path/to/image/nibetaseries-<version>.simg \
                              nibs -c WhiteMatter CSF \
                                    --participant-label 001 \
                                    -w {work_dir} \
                                    -a {atlas_mni_file} \
                                    -l {atlas_tsv} \
                                    {bids_dir} \
                                    fmriprep \
                                    {out_dir} \
                                    participant

.. Note::

  The Singularity example depicted above assumes that Singularity is configured
  in such a way that folders on your host are not automatically bound (mounted or exposed).
  In case they are, the *-B* lines can be neglected and paths on your host should be
  indicated regarding *-w*, *bids_dir* and *out_dir*.


Manually prepared environment (Python 3.5+)
-------------------------------------------

In order to install the NiBetaSeries Python module type the
following in the command line:

::

    pip3 install "nibetaseries==X.Y.Z"

Afterwards, NiBetaSeries can be run as follows from the command line:

::

  nibs -c WhiteMatter CSF \
        --participant-label 001 \
        -w {work_dir} \
        -a {atlas_mni_file} \
        -l {atlas_tsv} \
        {bids_dir} \
        fmriprep \
        {out_dir} \
        participant
