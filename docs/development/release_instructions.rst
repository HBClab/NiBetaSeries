.. _release_instructions:

====================
Release Instructions
====================

In order to create a release for NiBetaSeries, we must make sure the pre-conditions are
met, and that we follow the release instructions.
We follow `semantic versioning <https://semver.org/>`_ to define whether the release
should be a patch or a minor version.
Please note while the major version is ``0``, this project will be considered to be
in development and backwards incompatible changes may occur without incrementing the
major version.

Pre-Conditions
--------------

1. Continuous integration (circleci and travisci) are passing tests
2. Code coverage is above 70%
3. There has been at least one pull request merged since the previous release.

Instructions
------------

1. Create a branch called ``rel_vX.Y.ZrcN`` with X, Y, and Z replaced with the proposed version.
   N represents the current release candidate, starting with the number 1.
2. We use `Release Drafter <https://github.com/apps/release-drafter>`_
   to annotate the release notes in github.
3. Copy the generated text into ``CHANGELOG.rst`` with a sub-heading that indicates
   version, month, day, and year.
   Add information underneath the header thanking contributors and give brief summary
   of the changes made.
   Add and commit ``CHANGELOG.rst``.
4. Run ``create_long_description.py`` from the base of the repository.
   Add and commit ``long_description.rst``.
5. Push the branch onto your forked repository and open a pull request.
6. Name the Pull Request ``[REL] vX.Y.ZrcN``
7. Create a checklist to ensure:

    - ``CHANGELOG.rst`` is finalized
    - ``long_description.rst`` is finalized
    - new contributors are added to ``.zenodo.json``
    - ask repeat contributors if they want to be a creator.
    - other issues that pop up during the release (for example, deployment is not working)

8. After all creators review ``CHANGELOG.rst`` and optionally other changes, merge the pull request.
9. Go to the Releases section on the repository and create a new release.
10. Copy the brief summary from ``CHANGELOG.rst`` and add it below the ``CHANGES`` section
    in the text provided by Release Drafter.
11. Tag the release as ``vX.Y.ZrcN`` where X, Y, and Z are the major, minor, and patch numbers
    respectively, and N is the release candidate number starting with 1.
12. Mark the release as a pre-release.
13. Create the release and check if nibetaseries is being built and deployed on ``dockerhub``
    and ``pypi`` correctly.
14. If not successful, create another branch called ``rel_vX.Y.ZrcN`` with N being incremented.
15. Make the necessary changes to fix deployment and go back to step 5.
16. If successful, create a new tag ``vX.Y.Z`` copying all release drafter information
    from the last successful release candidate.

Yay! If you've followed these instructions, you'll be a release pro in no time.
