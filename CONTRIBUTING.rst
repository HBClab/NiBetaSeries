============================
Contributing to NiBetaSeries
============================

**Welcome to the NiBetaSeries repository!**

*We're so excited you're here and want to
contribute.*

NiBetaSeries calculates betaseries correlations using python!
We hope that these guidelines are designed to make it as easy
as possible to contribute to NiBetaSeries
and the broader Brain Imaging Data Structure (BIDS) community.
If you have any questions that aren't discussed below,
please let us know through one of the many
ways to `get in touch <#get-in-touch>`__.

Table of contents
-----------------

Been here before? Already know what you're looking for in this guide?
Jump to the following sections:

-  `Joining the BIDS community <#joining-the-bids-community>`__
-  `Check out the BIDS Starter Kit <#check-bids-starter-kit>`__
-  `Get in touch <#get-in-touch>`__
-  `Contributing through GitHub <#contributing-through-github>`__
-  `Where to start: wiki, code and
   templates <#where-to-start-wiki-code-and-templates>`__
-  `Where to start: issue labels <#where-to-start-issue-labels>`__
-  `Make a change with a pull
   request <#making-a-change-with-a-pull-request>`__
-  `Example pull request <#example-pull-request>`__
-  `Recognizing contributions <#recognizing-contributions>`__

Joining the BIDS community
--------------------------

BIDS - the `Brain Imaging Data
Structure <http://bids.neuroimaging.io>`__ - is a growing community of
neuroimaging enthusiasts, and we want to make our resources accessible
to and engaging for as many researchers as possible.
NiBetaSeries will hopefully play a small part towards introducing people
to BIDS and help the broader community.

We therefore require that all contributions **adhere to our** `Code of
Conduct <CODE_OF_CONDUCT.md>`__.

How do you know that you're a member of the BIDS community? You're here!
You know that BIDS exists! You're officially a member of the community.
It's THAT easy! Welcome!

Check out the BIDS Starter Kit
------------------------------

If you're new to BIDS make sure to check out the amazing  `BIDS Starter Kit <https://github.com/INCF/BIDS-Starter-Kit>`_.

Get in touch
------------

There are lots of ways to get in touch with the team maintaining NiBetaSeries
if you have general questions about the BIDS ecosystem.
For specific questions about NiBetaSeries, please see the practical guide
(Currently the main contact is James Kent)

-  Message jdkent on the `brainhack slack <https://brainhack.slack.com/messages/C8RG7F6PN>`__
-  Click `here <https://brainhack-slack-invite.herokuapp.com>`__ for an
   invite to the slack workspace.
-  The `BIDS mailing
   list <https://groups.google.com/forum/#!forum/bids-discussion>`__
-  Via the `Neurostars forum <https://neurostars.org/tags/bids>`__.
    -  **This is our preferred way to answer questions so that others who
       have similar questions can benefit too!** Even if your question is
       not well-defined, just post what you have so far and we will be able
       to point you in the right direction!

Contributing through GitHub
---------------------------

`git <https://git-scm.com>`__ is a really useful tool for version
control. `GitHub <https://github.com>`__ sits on top of git and supports
collaborative and distributed working.

We know that it can be daunting to start using git and GitHub if you
haven't worked with them in the past, but the NibetaSeries
maintainer(s) are here to help you figure out any of the jargon or
confusing instructions you encounter!

In order to contribute via GitHub you'll need to set up a free account
and sign in. Here are some
`instructions <https://help.github.com/articles/signing-up-for-a-new-github-account/>`__
to help you get going. Remember that you can ask us any questions you
need to along the way.

Writing in markdown
-------------------

GitHub has a helpful page on `getting started with writing and
formatting on
GitHub <https://help.github.com/articles/getting-started-with-writing-and-formatting-on-github>`__.

Most of the writing that you'll do in github will be in
`Markdown <https://daringfireball.net/projects/markdown>`__. You can
think of Markdown as a few little symbols around your text that will
allow GitHub to render the text with a little bit of formatting. For
example you could write words as bold (``**bold**``), or in italics
(``*italics*``), or as a `link <https://www.youtube.com/watch?v=dQw4w9WgXcQ>`__ to another webpage.

Writing in ReStructuredText
---------------------------

This file and the rest of the documentation files in this project
are written using `ReStructuredText <http://docutils.sourceforge.net/rst.html#user-documentation>`__.
This is another markup language that interfaces with `sphinx <http://www.sphinx-doc.org/en/master/index.html>`__,
a documentation generator.
Sphinx is used on `ReadTheDocs <https://docs.readthedocs.io/en/latest/index.html>`__,
a documentation hosting service.
Putting it all together, ReadTheDocs is an online documentation hosting service
that uses sphinx, and sphinx is a documentation generation service that uses
ReStructuredText to format the content.
What a mouthfull!

Where to start: issue labels
----------------------------

The list of labels for current issues can be found
`here <https://github.com/HBClab/NiBetaSeries/labels>`__ and includes:

-  |help-wanted| *These issues contain a task that a member of the team
   has determined we need additional help with.*

   If you feel that you can contribute to one of these issues, we
   especially encourage you to do so!

-  |question| *These issues contain a question that you'd like to have
   answered.*

   There are `lots of ways to ask questions <#get-in-touch>`__ but
   opening an issue is a great way to start a conversation and get your
   answer. Ideally, we'll close it out by `adding the answer to the
   docs <https://nibetaseries.readthedocs.io/en/latest/>`__!

-  |good-first-issue| *These issues are particularly appropriate if it
   is your first contribution to NiBetaSeries, or to GitHub
   overall.*

   If you're not sure about how to go about contributing, these are good
   places to start. You'll be mentored through the process by the
   maintainers team. If you're a seasoned contributor, please select a
   different issue to work from and keep these available for the newer
   and potentially more anxious team members.

-  |feature| *These issues are suggesting new features that can be
   added to the project.*

   If you want to ask for something new, please try to make sure that
   your request is distinct from any others that are already in the
   queue (or part of NiBetaSeries!). If you find one that's similar
   but there are subtle differences please reference the other
   enhancement in your issue.

-  |documentation| *These issues relate to improving or updating the
   documentation.*

   These are usually really great issues to help out with: our goal is
   to make it easy to understand BIDS without having to ask anyone any
   questions! Documentation is the ultimate solution

-  |bug| *These issues are reporting a problem or a mistake in the
   project.*

   The more details you can provide the better! If you know how to fix
   the bug, please open an issue first and then `submit a pull
   request <#making-a-change-with-a-pull-request>`__

   We like to model best practice, so NiBetaSeries itself is
   managed through these issues. We may occasionally have some to
   coordinate some logistics.

Making a change with a pull request
-----------------------------------

We appreciate all contributions to NiBetaSeries. **THANK YOU**
for helping us build this useful resource.

Remember that if you're adding information to the
`wiki <#wiki>`__ you **don't need to submit a pull request**. You can
just log into GitHub, navigate to the
`wiki <https://github.com/HBClab/NiBetaSeries/wiki>`__ and click the
**edit** button.

If you're updating the `code <#code>`__,
the following steps are a guide to help you
contribute in a way that will be easy for everyone to review and accept
with ease.

1. `Comment on an existing issue or open a new issue referencing your addition <https://github.com/HBClab/NiBetaSeries/issues>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This allows other members of the NiBetaSeries team to confirm that
you aren't overlapping with work that's currently underway and that
everyone is on the same page with the goal of the work you're going to
carry out.

`This blog <https://www.igvita.com/2011/12/19/dont-push-your-pull-requests>`__
is a nice explanation of why putting this work in up front is so useful
to everyone involved.

2. `Fork <https://help.github.com/articles/fork-a-repo>`__ the `NiBetaSeries repository <https://github.com/HBClab/NiBetaSeries>`__ to your profile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is now your own unique copy of NiBetaSeries. Changes here
won't affect anyone else's work, so it's a safe space to explore edits
to the code!

Make sure to `keep your fork up to
date <https://help.github.com/articles/syncing-a-fork>`__ with the
master repository, otherwise you can end up with lots of dreaded `merge
conflicts <https://help.github.com/articles/about-merge-conflicts>`__.

3. `Clone your forked <https://help.github.com/articles/cloning-a-repository/>`__ NiBetaSeries to your work machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that you have your own repository to explore you should clone
it to your work machine so you can easily
edit the files::

    # clone the repository
    git clone https://github.com/YOUR-USERNAME/NiBetaSeries
    # change directories into NiBetaSeries
    cd NiBetaSeries
    # add the upstream repository (i.e. https://github.com/HBClab/NiBetaSeries)
    git remote add upstream https://github.com/HBClab/NiBetaSeries

4. Make the changes you've discussed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try to keep the changes focused. If you submit a large amount of work in
all in one go it will be much more work for whomever is reviewing your
pull request. `Help them help
you <https://media.giphy.com/media/uRb2p09vY8lEs/giphy.gif>`__

This project requires you to "branch out" and make `new
branch <https://help.github.com/articles/creating-and-deleting-branches-within-your-repository>`__
and a `new issue <https://github.com/HBClab/NiBetaSeries/issues>`__ to
go with it if the issue doesn't already exist.

Example::

    # create the branch on which you will make your issues
    git checkout -b your_issue_branch

5. Run the tests
~~~~~~~~~~~~~~~~

When you're done making changes, run all the checks, doc builder and spell checker with `tox <http://tox.readthedocs.io/en/latest/install.html>`_.
First you will install all the development requirements
for the project with pip::

    pip install requirements-dev.txt

Then you can run tox by simply typing::

    tox

If the checks fail and you know what went wrong,
make the change and run tox again.
If you are not sure what the error is, go ahead to step 6.

.. note:: tox doesn't work on everyone's machine, so don't worry about getting the tests
    working on your machine.

6. Add/Commit/Push the changes to the NiBetaSeries repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've made the changes on your branch you are ready to
1) add the files to be tracked by git
2) commit the files to take a snapshot of the branch, and
3) push the changes to your forked repository.
You can do complete the add/commit/push process
following this `github help page <https://help.github.com/articles/adding-a-file-to-a-repository-using-the-command-line/>`__.

7. Submit a `pull request <https://help.github.com/articles/creating-a-pull-request>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A member of the NiBetaSeries team will review your changes to
confirm that they can be merged into the main codebase.

A `review <https://help.github.com/articles/about-pull-request-reviews>`__
will probably consist of a few questions to help clarify the work you've
done. Keep an eye on your github notifications and be prepared to join
in that conversation.

You can update your `fork <https://help.github.com/articles/fork-a-repo>`__ of the NiBetaSeries
`repository <https://github.com/HBClab/NiBetaSeries>`__
and the pull request will automatically update with those changes. You
don't need to submit a new pull request when you make a change in
response to a review.

GitHub has a `nice
introduction <https://guides.github.com/introduction/flow>`__ to the
pull request workflow, but please `get in touch <#get-in-touch>`__ if
you have any questions.

NiBetaSeries coding style guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whenever possible, instances of Nodes and Workflows should use the same names
as the variables they are assigned to.
This makes it easier to relate the content of the working directory to the code
that generated it when debugging.

Workflow variables should end in `_wf` to indicate that they refer to Workflows
and not Nodes.
For instance, a workflow whose basename is `myworkflow` might be defined as
follows::

    from nipype.pipeline import engine as pe

    myworkflow_wf = pe.Workflow(name='myworkflow_wf')


If a workflow is generated by a function, the name of the function should take
the form `init_<basename>_wf`::

    def init_myworkflow_wf(name='myworkflow_wf):
        workflow = pe.Workflow(name=name)
        ...
        return workflow

    myworkflow_wf = init_workflow_wf(name='myworkflow_wf')


If multiple instances of the same workflow might be instantiated in the same
namespace, the workflow names and variables should include either a numeric
identifier or a one-word description, such as::

    myworkflow0_wf = init_workflow_wf(name='myworkflow0_wf')
    myworkflow1_wf = init_workflow_wf(name='myworkflow1_wf')

    # or

    myworkflow_lh_wf = init_workflow_wf(name='myworkflow_lh_wf')
    myworkflow_rh_wf = init_workflow_wf(name='myworkflow_rh_wf')


Recognizing contributions
-------------------------

BIDS follows the
`all-contributors <https://github.com/kentcdodds/all-contributors#emoji-key>`__
specification, so we welcome and recognize all contributions from
documentation to testing to code development. You can see a list of
current contributors in the `BIDS
specification <https://docs.google.com/document/d/1HFUkAEE-pB-angVcYe6pf_-fVf4sCpOHKesUvfb8Grc/edit#heading=h.hds2i7ii7hjo>`__.

Thank you!
----------

You're awesome.

*— Based on contributing guidelines from the*
`STEMMRoleModels <https://github.com/KirstieJane/STEMMRoleModels>`__
*project.*

.. |help-wanted| image:: https://img.shields.io/badge/-help%20wanted-%23128A0C.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/help%20wanted
.. |Question| image:: https://img.shields.io/badge/-question-%23cc317c.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/question
.. |invalid| image:: https://img.shields.io/badge/-invalid-%23e6e6e6.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/invalid
.. |good-first-issue| image:: https://img.shields.io/badge/-good%20first%20issue-%239cdb4a.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/good%20first%20issue
.. |duplicate| image:: https://img.shields.io/badge/-duplicate-cccccc.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/duplicate
.. |enhancement| image:: https://img.shields.io/badge/-enhancement-%2384b6eb.svg
   :target| https://github.com/HBClab/NiBetaSeries/labels/enhancement
.. |feature| image:: https://img.shields.io/badge/-feature-%239d2cd6.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/feature
.. |wontfix| image:: https://img.shields.io/badge/-wontfix-8bf4e3.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/wontfix
.. |hackathon| image:: https://img.shields.io/badge/-hackathon-%23463ea3.svg
   |target| https://github.com/HBClab/NiBetaSeries/labels/hackathon
.. |documentation| image:: https://img.shields.io/badge/-documentation-%2393f9a7.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/documentation
.. |bug| image:: https://img.shields.io/badge/-bug-ee0701.svg
   :target: https://github.com/HBClab/NiBetaSeries/labels/bug
