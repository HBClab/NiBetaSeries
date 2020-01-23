.. _faq:

==========================
Frequently Asked Questions
==========================


Does NiBetaSeries work with output from old fMRIPrep (< v1.2.0)?
----------------------------------------------------------------
Yes, NiBetaSeries will currently work with older version of fMRIPrep.
However, this will not continue to be the case.
To rename your files, you can use renameOldFMRIPREP_.

.. _renameOldFMRIPREP: https://github.com/HBClab/renameOldFMRIPREP


How do I just get the beta maps, not the correlation matrices?
--------------------------------------------------------------
Exclude both the atlas (``-a``) and lookup table (``-l``) options
if you only want the beta maps.