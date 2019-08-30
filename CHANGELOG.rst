.. _changelog:

0.3.0 (August 29, 2019)
=======================

Thanks to @PeerHerholz and @njvack for their contributions on this release.
Special thanks to @snastase for being a great reviewer and improving the project
overall.
This release is special because it will be published in the
Journal of Open Source Software (JOSS).
One condition of this is that the authors on the paper be the only authors in the zenodo file.
I will modify the authors listed on the zenodo file for this release,
but I will add all contributors back on for the subsequent release.

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
========================

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
=========================

Quick bug fixes, one related to updating the
nipype dependency to a newer version (1.1.5)

* [ENH] add nthreads option and make multiproc the default (#81) @jdkent
* [FIX] add missing comma in hrf_models (#83) @jdkent

0.2.1 (November 13, 2018)
=========================

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
=========================

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


0.1.0 (2018-06-08)
==================

* First release on PyPI.
