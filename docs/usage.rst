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

.. _example-one:

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
    --estimator lss \
    --description-label AROMAnonaggr \
    --hrf-model 'glover + derivative + dispersion'

In this example we have our top-level BIDS directory ``/home/james/bids``,
and our derivatives directory ``/home/james/bids/derivatives``.
``nibs`` currently assumes that ``derivatives`` is immediately underneath
the top-level BIDS directory.

- The 1st positional argument is the BIDS directory (``/home/james/bids``)
- The 2nd positional argument is the derivatives pipeline that was used
  to preprocess your data.
  In this case we are using ``fmriprep``.
- The 3rd positional argument determines where the desired output of ``nibs``
  should go. These are the output files you will use later on for analysis.
  Here, the directory is:
  ``/home/james/bids/derivatives/betaSeries/schaefer_parcel-400_network-17``
- The 4th positional argument specifies whether we are running participant-
  or group-level analyses; since group-level analyses are not yet implemented,
  ``participant`` is the only option.
- Within the derivatives directory, we have the atlas (``-a``) and
  lookup table (``-l``) in an atlas directory.
  The atlas is in MNI space and the look up table has a row per unique parcel
  in the atlas.
- The work directory (``-w``) specifies where all the intermediate outputs
  go; these are useful for making sure ``nibs`` ran correctly,
  but are not necessary to keep after you are reasonably confident
  ``nibs`` worked as expected.
- The confounds (``-c``) we select are column names from the ``*_confounds.tsv`` file.
  See the `fmriprep documentation
  <https://fmriprep.readthedocs.io/en/stable/outputs.html#confounds>`_ on confounds for details.
- ``--nthreads`` tells us across how many thread to parallelize ``nibs``; in this
  example we use 32 threads!
- ``--estimator`` tells us we are using ``lss`` or Least Squares Separate for
  the generation of the betas.
- If there were multiple types of derivatives output from a preprocessing
  application (like ``fmriprep``), you may only be interested in analyzing
  one variant; in this scenerio, we are only interested in analyzing images denoised
  by ``ICA-AROMA``, denoted by ``--description-label``.
- The HRF model argument (``--hrf-model``) passes all the available options
  from `nistats <https://nistats.github.io/index.html>`_.

.. _example-two:

Example 2
~~~~~~~~~

.. code-block:: bash

    nibs \
    /home/james/bids/ \
    fmriprep \
    /home/james/bids/derivatives \
    participant
    --participant-label 001 \
    -w /tmp/work \
    -c white_matter csf cosine01 cosine02 cosine03 cosine04 cosine05 cosine06 cosine07 \
    --nthreads 32 \
    --estimator lsa \
    --hrf-model 'glover'

In this example, we are not interested in generating correlation matrices, but
we are interested in the beta maps.
Since the beta maps are given by default, we need remove the correlation output.
We can remove the correlation matrix output by removing the ``-l`` and ``-a`` options.
Another significant difference with :ref:`example-one` is the inclusion of ``--participant-label``.
This option says we only want to run ``nibs`` on participant ``sub-001`` in the bids dataset.
