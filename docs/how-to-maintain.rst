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

You can add a suffix to signal more information on the current version.

* Use ``0.0.1dev0`` to signal that the release is a development version which is
  currently tested and to be released soon. Increment the last digit for multiple
  development versions.

.. note::

   The development suffix is not separated with a dot from the patch version as this
   does not comply with the publishing process on anaconda.org.*


Branching Model
---------------

The branching model for GETTSIM is very simple.

1. The master branch is the target of ongoing development. Every PR should be merged
   into master.

   (The only deviation can happen with respect to backports. See :ref:`backports` for
   more.)

2. There can exist branches for minor versions called, for example, ``0.1.``. The
   branches contain changes, e.g. backports, which are not released yet. To find out how
   to release the next patch version, see the following section. If there are no
   additional changes waiting to be released, the branches should be deleted for
   clarity.


.. _releases:

How To Release
--------------

To release a new version of GETTSIM, do the following.

1. To start a new release for version ``0.2.1``, create a new milestone with the version
   as its name on Github to collect issues and PRs which should be included in the new
   version.

2. Call a halt on changes to the master branch. Make sure all changes to the master
   branch since the last version are included in the milestone.

**Here, we have to decide whether we allows pushing to master for releases or not. Then,
we can use bump2version to create a tagged commit. Otherwise, we stick to PRs and create
the tag via Github. I would go with the latter.**

3. Create a PR to finalize the new release.

   1. Update ``CHANGES.rst`` with all necessary information regarding the new release.
   2. Use ``bump2version [major|minor|patch]`` to increment all version strings.
   3. Merge it.

4. Go to the `page for releases <https://github.com/iza-institute-of-labor-economics/
   gettsim/releases>`_ and draft a new release. The tag and title become ``v0.2.1``.
   Make sure to target the master branch. A description is not necessary as the most
   important information lies in ``CHANGES.rst``.

   Release the new version by clicking "Publish release".


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

In the following we will consider an example where GETTSIM stable version is 0.2.0.
Version 0.2.1 is currently developed on the master branch but not released. And a bug
fix was found which should be backported to minor version 0.1 which latest patch version
is 8.

1. Create a PR which targets the master branch and includes the bug fix which should be
   backported.
2. Add a note to the release notes for version 0.1.9.
3. Add a label ``backport-to-0.1.9`` to the PR.
4. Squash merge the PR into master and note down the commit sha.
5. Create a new PR against branch 0.1.x. Either the branch exists or create the branch
   from the last released patch version 0.1.8. Call the branch for the PR
   ``backport-<#pr>`` where #pr is the PR number.
6. Use ``git cherrypick -x <commit-sha>`` with the aforementioned commit sha to apply
   the fix to the branch. Solve any merge conflicts, etc..
7. Add the PR to the milestone for version 0.1.9 so that all changes for a new release
   can be collected.
8. Follow :ref:`releases` to release 0.1.9.
