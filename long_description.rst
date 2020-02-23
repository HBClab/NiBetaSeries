.. _readme:

============
NiBetaSeries
============

If you are viewing this file on GitHub, please see our
`readthedocs page <https://nibetaseries.readthedocs.io>`_
for links to render properly.



What is NiBetaSeries?
---------------------
NiBetaSeries is BIDS_-compatible `application <https://bids-apps.neuroimaging.io/>`_
that calculates betaseries correlations.
In brief, a beta coefficient (i.e., parameter estimate) is calculated
for each trial (or event) resulting in a series of betas ("betaseries")
that can be correlated across regions of interest.

Why should I use it?
--------------------
There are potential insights hidden in your task fMRI data.
Rest fMRI enjoys a multitude of toolboxes which can be applied to task fMRI
with some effort, but there are not many toolboxes that focus on making
betaseries.
Betaseries can then be used for correlations/classifications and
a multitude of other analyses.
While a couple alternatives exist (pybetaseries_ and BASCO_), NiBetaSeries
is the only application to interface with BIDS_ organized data with the goal
of providing a command-line application experience like fMRIPrep_.

What does NiBetaSeries give me?
-------------------------------
Currently NiBetaSeries returns the beta series images and optionally
symmetric z-transformed correlation matrices with an entry for each
parcel defined in the atlas.

.. note:: The betas (i.e., parameter estimates) are generated using either
    the "Least Squares Separate" or "Least Squares All" procedures.
    Please read the betaseries page for more background information.

What do I need to run NiBetaSeries?
-----------------------------------
NiBetaSeries takes BIDS_ and preprocessed data as input that satisfy the
`BIDS derivatives specification <http://bit.ly/2vKeKcp>`_.
In practical terms, NiBetaSeries uses the output of fMRIPrep_,
a great BIDS-compatible preprocessing tool.
NiBetaSeries requires the input and the atlas to already
be in the same space (e.g., MNI space).
For more details, see usage and the tutorial
(sphx_glr_auto_examples_plot_run_nibetaseries.py)

Get Involved
------------
This is a very young project that still needs some tender loving care to grow.
That's where you fit in!
If you would like to contribute, please read our code_of_conduct
and contributing page (contributing).

Thanks!
-------
This project heavily leverages `nipype <http://nipype.readthedocs.io/en/latest/>`_,
`nilearn <https://nilearn.github.io/>`_, `pybids <https://bids-standard.github.io/pybids/>`_, and
`nistats <https://nistats.github.io/>`_ for development.
Please check out their pages and support the developers.

.. _BASCO: https://www.nitrc.org/projects/basco/
.. _pybetaseries: https://github.com/poldrack/pybetaseries
.. _BIDS: http://bids.neuroimaging.io/
.. _fMRIPrep: http://fmriprep.readthedocs.io/en/latest/

.. _changelog:

=========
CHANGELOG
=========

0.4.3 (February 22, 2020)
-------------------------
Bug fix and enhancement release.
Made a quick decision to remove volumes that have large unstable beta estimates.

* [FIX] allow atlas arguments to be None (#283) @jdkent
* [FIX] bump nipype version (#280) @jdkent
* [ENH] censor invalid volumes (#277) @jdkent
* [ENH] allow regex for confound specification and impute derivatives (#273) @jdkent

0.4.2 (January 23, 2020)
------------------------
Bug fix and maintenance release.

* [DOC] emphasize beta map analysis (#270) @jdkent
* [FIX] allow other spaces (#269) @jdkent
* [FIX] less strict beta map generation (#262) @jdkent
* [ENH] handle all confound NaNs (#255) @jdkent
* [ENH] improve bids indexing (#253) @jdkent
* [FIX] allow "sub-" prefix (#256) @jdkent

0.4.1 (December 16, 2019)
-------------------------
Bug fix and maintenance release.

* [MAINT] refactor and increase tests for run.py (#249) @jdkent
* [FIX] allow flexible derivatives location (#247) @jdkent
* [ENH] create useful error message when images are not found  (#246) @jdkent
* [MAINT] fix nistats dependency  (#245) @jdkent

0.4.0 (October 07, 2019)
------------------------
This has been a busy month for NiBetaSeries.
We have two more methods for calculating betas (LSA and FS),
and LSS has been modified to account for separate conditions.
All of this great work is thanks to @tsalo.

The second major change is the refactor of how we read from
the FMRIPREP directory, previously we assumed results from
fmriprep version (< v1.2.0), but now we only support files output
from fmriprep (>= v1.2.0).
If you have results from an older version of fmriprep, check our
FAQ for a potential solution.

The third major change is the generation of a citation template,
so you can easily populate your methods section with the appropriate information.
Again, thanks to @tsalo for this marvelous contribution.

The fourth and final major change (in no particular order), is passing the
beta series image maps directly to the output directory, no longer requiring the
user to have an atlas and a lookup table to use NiBetaSeries.
This will allow users to use the beta series image maps for whatever downstream
analysis they wish.

Thank you to all the contributors mentioned below for improving NiBetaSeries
through documentation fixes and other code changes.

An unsung hero is @PeerHerholz for code review and
beneficial recommendations for the future of NiBetaSeries, Thank you!
Also not listed is @mwvoss for opening issue #123.
Making a good issue is work and should be recognized, thank you!

While I have almost certainly missed giving thanks to everyone that
has helped, please know I appreciate your contributions and I'm
thankful you took some time out of your day to help this project grow.

* [DOC] update instructions with template checklist (#242) @jdkent
* [FIX] update code-server version (#238) @jdkent
* [DOC] Generate citable boilerplates for workflows (#205) @tsalo
* [DOC] Clarify in demo that you are stripping color codes #123 (#234) @ipacheco-uy
* [DOC] Fix documentation headers (#235) @atrievel
* [FIX] add nano to dev container (#233) @pranesh-sp
* [DOC] add lsa section (#231) @jdkent
* [DOC] add joss badge (#229) @zkhan12
* [ENH,DOC] add development documentation section (#222) @jdkent
* [DOC,FIX] add fake img and lut to participant workflow (#225) @jdkent
* [ENH] Implement finite BOLD response- separate (FS) modeling (#204) @tsalo
* [MAINT] allow more lenience for pull requests (#223) @jdkent
* [ENH] Make atlases optional (#213) @jdkent
* [FIX,DOC] make title for changelog (#221) @jdkent
* [MAINT] make travisci more efficient (#216) @jdkent
* [FIX] make codecov yaml valid (#220) @jdkent
* [FIX] show binder badge on readthedocs (#219) @jdkent
* [ENH,DOC] sphinx gallery binder (#217) @jdkent
* [MAINT] make codecov more lenient (#215) @jdkent
* [FIX] use scope=derivatives in collect_data (#212) @jdkent
* [FIX] respond to suggested edits (#206) @jdkent
* [ENH] Implement least squares- all (LSA) modeling (#202) @tsalo
* [TST] add more tests (#201) @jdkent
* [FIX, DOC] Rename low-pass filter to high-pass filter (#198) @tsalo
* [MAINT] explicitly set codecov settings (#200) @jdkent
* [ENH,FIX] refactor bids file processing (#193) @jdkent
* [ENH] Separate other conditions in LSS model (#191) @tsalo

0.3.2 (September 04, 2019)
--------------------------

This release is special because it will be published in the
Journal of Open Source Software (JOSS).
One condition of this is that the authors on the paper be the only authors in the zenodo file.
I will modify the authors listed on the zenodo file for this release,
but I will add all contributors back on for the subsequent release.

* [MAINT] fix zenodo file

0.3.1 (September 04, 2019)
--------------------------

Changes to installation and documentation, but no functional code changes.

* [DOC] address review comments (#185) @jdkent
* [DOC] add everyone to contributors in the zenodo file (#188) @jdkent
* [MAINT] Change Installation Method (#187) @jdkent
* [ENH] add code server (#182) @jdkent
* [MAINT] build tags (#183) @jdkent

0.3.0 (August 29, 2019)
-----------------------

Thanks to @PeerHerholz and @njvack for their contributions on this release.
Special thanks to @snastase for being a great reviewer and improving the project
overall.

* [ENH] reduce focus on parcellations (#179) @jdkent
* [FIX] generalized -> general linear model description (#178) @jdkent
* [DOC] Add math (#177) @jdkent
* [FIX] remove .git from the binder url (#175) @jdkent
* [FIX] add pypiwin32 as conditional dependency (#173) @jdkent
* [FIX] add readthedocs config file (#174) @jdkent
* [DOC] Minor changes to documentation text (#163) @snastase
* [MAINT] fix tagging/pushing docker images (#160) @jdkent
* [FIX] binder ci triggers (#159) @jdkent
* [ENH] add binder (#158) @jdkent
* [MAINT] Change Install Strategy (#157) @jdkent
* [DOC] Clarify Documentation (#156) @jdkent
* [FIX] Only hyphens for commandline parameters (#155) @jdkent
* [DOC] add concrete example of nibs (#154) @jdkent
* [DOC] add references (#153) @jdkent
* [MAINT] build docs on circleci (#152) @jdkent
* [MAINT] temporary fix to dockerfile (#150) @jdkent
* [MAINT] require python3 (#147) @jdkent
* [ENH] add visualizations (#148) @jdkent
* [ENH] Add Docker and Singularity Support (#140) @PeerHerholz
* [DOC] edit docs (#142) @jdkent
* [DOC] Tiny tweak to README (#141) @njvack
* [WIP] JOSS Paper (#122) @jdkent

0.2.3 (January 29, 2019)
------------------------

Various documentation and testing changes.
We will be using readthedocs going forward and not doctr.

* [FIX] Remove high_pass references from documentation (#90) @RaginSagan
* [FIX] Update betaseries.rst (#91) @ilkayisik
* [ENH] autogenerate test data (#93) @jdkent
* [FIX] add codecov back into testing (#94) @jdkent
* [FIX] refactor dependencies (#95) @jdkent
* [ENH] add example (#99) @jdkent
* [FIX] first pass at configuring doctr (#100) @jdkent
* [FIX] configure doctr (#101) @jdkent
* [FIX] track version with docs (#102) @jdkent
* [ENH] add sphinx versioning (#104) @jdkent
* [FIX] first pass at simplifying example (#106) @jdkent
* [FIX] add master back in to docs (#107) @jdkent
* [MAINT] use readthedocs (#109) @jdkent
* [DOC] add explicit download instruction (#112) @jdkent
* [FIX] add graphviz as dependency for building docs (#115) @jdkent
* [FIX] remove redundant/irrelevant doc building options (#116) @jdkent
* [DOC] fix links in docs (#114) @PeerHerholz
* [FIX,MAINT] rm 3.4 and test add 3.7 (#121) @jdkent
* [FIX] pybids link (#120) @PeerHerholz
* [FIX] syntax links (#119) @PeerHerholz

0.2.2 (November 15, 2018)
-------------------------

Quick bug fixes, one related to updating the
nipype dependency to a newer version (1.1.5)

* [ENH] add nthreads option and make multiproc the default (#81) @jdkent
* [FIX] add missing comma in hrf_models (#83) @jdkent

0.2.1 (November 13, 2018)
-------------------------

Large thanks to everyone at neurohackademy that helped make this a reality.
This release is still a bit premature because I'm testing out
my workflow for making releases.

* [ENH] Add link to Zenodo DOI (#57) @kdestasio
* [ENH] run versioneer install (#60) @jdkent
* [FIX] connect derivative outputs (#61) @jdkent
* [FIX] add CODEOWNERS file (#63) @jdkent
* [FIX] Fix pull request template (#65) @kristianeschenburg
* [ENH] Update CONTRIBUTING.rst (#66) @PeerHerholz
* [FIX] ignore sourcedata and derivatives directories in layout (#69) @jdkent
* [DOC] Added zenodo file (#70) @ctoroserey
* [FIX] file logic (#71) @jdkent
* [FIX] confound removal (#72) @jdkent
* [FIX] Find metadata (#74) @jdkent
* [FIX] various fixes for a real dataset (#75) @jdkent
* [ENH] allow confounds to be none (#76) @jdkent
* [ENH] Reword docs (#77) @jdkent
* [TST] Add more tests (#78) @jdkent
* [MGT] simplify and create deployment (#79) @jdkent

0.2.0 (November 13, 2018)
-------------------------

* [MGT] simplify and create deployment (#79)
* [TST] Add more tests (#78)
* [ENH] Reword docs (#77)
* [ENH] allow confounds to be none (#76)
* [FIX] various fixes for a real dataset (#75)
* [FIX] Find metadata (#74)
* [FIX] confound removal (#72)
* [WIP,FIX]: file logic (#71)
* [DOC] Added zenodo file (#70)
* [FIX] ignore sourcedata and derivatives directories in layout (#69)
* [DOC] Update CONTRIBUTING.rst (#66)
* [FIX] Fix pull request template (#65)
* [FIX] add CODEOWNERS file (#63)
* [FIX] connect derivative outputs (#61)
* [MAINT] run versioneer install (#60)
* [FIX] Fix issue #29: Add link to Zenodo DOI (#57)
* [FIX] Fix issue #45: conform colors of labels (#56)
* [DOC] fix links in readme.rst (#55)
* [DOC] Added code of conduct (#53)
* [DOC] Add link to contributing in README (#52)
* [DOC] removed acknowledgments section of pull request template (#50)
* [TST] Add functional test (#49)
* [FIX] remove references to bootstrap (#48)
* [FIX] test remove base .travis.yml (#47)
* [ENH] removed data directory (#40)
* [ENH] Add pull request template (#41)
* [ENH] Update issue templates (#44)
* [DOC] Update contributing (#43)
* [DOC] README (where's the beef?) (#37)
* [MAINT] change jdkent to HBClab (#38)
* [FIX] pass tests (#14)
* [ENH] improve docs (#13)
* [DOC] add documentation (#11)
* [FIX] add graph (#10)
* [ENH] Refactor NiBetaSeries (#9)
* [ENH] Refactor (#2)

0.1.0 (June 08, 2018)
---------------------

* First release on PyPI.
