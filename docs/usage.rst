.. _usage:

=====
Usage
=====

Command-Line Arguments
----------------------

.. argparse::
   :ref: nibetaseries.cli.run.get_parser
   :prog: nibs
   :nodefault:
   :nodefaultconst:

Example Call(s)
---------------

If you want to see a full example on preparing data and running ``nibs``, see:
:ref:`sphx_glr_auto_examples_plot_run_nibetaseries.py`.

Example 1
~~~~~~~~~

.. code-block:: bash

    nibs \
    /home/james/bids/ \
    fmriprep \
    /home/james/bids/derivatives/betaSeries/schaefer_parcel-400_network-17 \
    participant
    -a /home/james/bids/derivatives/atlas/Schaefer2018_400Parcels_17Networks_order_FSLMNI152_2mm.nii.gz \
    -l /home/james/bids/derivatives/atlas/schaefer_parcel-400_network-17.tsv \
    -w /home/james/bids/derivatives/betaSeries/work_n17 \
    -c WhiteMatter CSF Cosine01 Cosine02 Cosine03 Cosine04 Cosine05 Cosine06 Cosine07 \
    --nthreads 32 \
    --variant AROMAnonaggr \
    --hrf-model 'glover + derivative + dispersion'

In this example we have our bids directory ``/home/james/bids``,
and our derivatives directory ``/home/james/bids/derivatives``.
``nibs`` currently assumes that ``derivatives`` is immediately underneath
the bids directory.

- The first positional argument is the bids directory (``/home/james/bids``)
- The second positional argument is the derivatives pipeline that was used
  to preprocess your data.
  In this case we are using ``fmriprep``.
- The third positional argument decides where the desired output of ``nibs``
  should go. These are the output files you will use later on for analysis.
  The directory is:
  ``/home/james/bids/derivatives/betaSeries/schaefer_parcel-400_network-17``
- The 4th positional argument specifies whether we are running participant
  or group level analyses, since group level analyses are not yet implemented,
  ``participant`` is the only real option.
- Within the derivatives directory, we have the atlas (``-a``) and
  lookup table (``-l``) in an atlas directory.
  The atlas is in MNI space and the look up table has a row per unique parcel
  in the atlas.
- The work directory (``-w``) specifies where all the intermediate outputs
  go that are useful for making sure ``nibs`` ran correctly,
  but are not necessary to keep after you are reasonably confident
  ``nibs`` worked as expected.
- The confounds (``-c``) we select are column names from the ``*_confounds.tsv`` file.
  See the `fmriprep documentation
  <https://fmriprep.readthedocs.io/en/stable/outputs.html#confounds>`_ on confounds for details.
- ``--nthreads`` tells us how parallelized we run ``nibs``, in this
  example we have access to 32 threads!
- If there were multiple types of derivatives output from a preprocessing
  application (like ``fmriprep``), you may only be interested in analyzing
  one variant.
  In this scenerio, we are only interested in analyzing images denoised
  by ``ICA-AROMA``.
- the hrf model (``--hrf-model``) passes all the available options
  from `nistats <https://nistats.github.io/index.html>`_.
