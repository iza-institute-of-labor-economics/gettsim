How To Maintain
===============

This document is dedicated to maintainers of GETTSIM.


Versioning
----------

GETTSIM adheres in large parts to `semantic versioning <https://semver.org>`_. Thus, for
a given version number ``major.minor.patch``

* ``major`` is incremented when you make incompatible API changes.
* ``minor`` is incremented when you add functionality which is backwards compatible.
* ``patch`` is incremented when you make backwards compatible bug fixes.

Branching Model
---------------

The branching model for GETTSIM is very simple.

1. New major and minor releases of GETTSIM are developed on the master branch. Changes
   dedicated to all versions should be merged into master first.

2. For older major and minor releases there exist branches for maintenance called
   ``0.1`` or ``1.3``. These branches are used to develop new patch versions.

   Once a minor version will not be supported anymore, the maintenance branch should be
   deleted.


.. _releases:

How To Release
--------------

To release a new version of GETTSIM, do the following.

1. To start the release for any new version, e.g., ``0.2.0``, `create a new milestone
   <https://github.com/iza-institute-of-labor-economics/gettsim/milestones/new>`_ with
   the version as its name on Github to collect issues and PRs. A consensus among
   developers determines the scope of the new release.

2. To finalize a release

   1. Update :ref:`changes` with all necessary information regarding the new release.
   2. Use ``bumpversion [major|minor|patch]`` to increment all version strings.
   3. Merge it to either the master or maintenance branch.

3. The following step assigns a version and documents the release on Github. Go to the
   `page for releases <https://github.com/iza-institute-of-labor-economics/
   gettsim/releases>`_ and draft a new release. The tag and title become ``vx.x.x``.
   Make sure to target the master or maintenance branch. A description is not necessary
   as the most important information is documented under :ref:`changes`. Release the new
   version by clicking "Publish release".

4. Check out the new release tag and run

   .. code-block:: bash

       $ python release.py

   which uploads the new release to the repository on
   https://anaconda.org/gettsim/gettsim.


.. _backports:

How To Backport
---------------

Backporting is the process of applying a change in future versions of GETTSIM to older
versions

Scope
^^^^^

As backports can introduce new regressions the scope is limited to critical bug fixes
and documentation changes. Performance enhancements and new features are not backported.

Procedure
^^^^^^^^^

In the following we will consider an example where GETTSIM's stable version is
``0.2.0``. Version ``0.3.0`` is currently developed on the master. And a critical bug
was found which should go both into ``0.3.0`` and ``0.2.0``.

1. Create a PR containing the bug fix which targets the master branch.
2. Add a note to the release notes for version 0.2.1.
3. Add a label ``backport-to-0.2.1`` to the PR.
4. Squash merge the PR into master and note down the commit sha.
5. Create a new PR against branch ``0.2``. Call the branch for the PR
   ``backport-<#pr>`` where #pr is the PR number.
6. Use ``git cherrypick -x <commit-sha>`` with the aforementioned commit sha to apply
   the fix to the branch. Solve any merge conflicts, etc..
7. Add the PR to the milestone for version ``0.2.1`` so that all changes for a new
   release can be collected.
8. Follow :ref:`releases` to release ``0.2.1``.


