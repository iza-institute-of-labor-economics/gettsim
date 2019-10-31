How To Contribute
=================

Contributions are always welcome. Everything ranging from small extensions of the
documentation to implementing new features is appreciated. Of course, the bigger the
change the more it is necessary to reach out to us in advance for an discussion. You can
start an discussion by `posting an issue <https://github.com/iza-institute-of-labor-
economics/gettsim/issues/new/choose>`_ which can be a bug report or a feature request or
something else.

To get acquainted with the code base, you can also check out the `documentation
<https://gettsim.readthedocs.io/en/latest/>`_ or our `issue tracker
<https://github.com/iza-institute-of-labor-economics/gettsim/issues>`_ for some
immediate and clearly defined tasks.

To contribute to the project, adhere to the following process.

1. The process starts differently for regular contributors and newcomers. As a
   contributor you might have been granted privileges to push to the GETTSIM repository.
   Thus, you can clone the repository directly using

   .. code-block:: bash

       $ git clone https://github.com/iza-institute-of-labor-economics/gettsim

   As a newcomer or infrequent contributor, you must first create a fork of GETTSIM
   which is a copy of the repository into your account where you have unlimited access.
   Go to the `Github page of GETTSIM
   <https://github.com/iza-institute-of-labor-economics/gettsim>`_ and click on the fork
   button in the upper right corner. Then, clone your fork onto your disk with

   .. code-block:: bash

       $ git clone https://github.com/<user>/gettsim

2. In the next step, go into the GETTSIM folder and set up the Python environment with

   .. code-block:: bash

       $ conda env create

   Then, activate the environment and install the current GETTSIM version in the
   repository in development mode. Also, install pre-commits which are checks before a
   commit is accepted.

   .. code-block:: bash

       $ conda activate gettsim
       $ conda develop .
       $ pre-commit install

3. We always develop new features in new branches. Thus, create a new branch by picking
   an appropriate name, e.g., ``kindergeld-freibetrag`` or ``ubi``. Make sure to branch
   off from master and not any other branch.

   .. code-block:: bash

       $ git checkout -b <branch-name>

4. Now, develop the new feature on this branch. Before you commit the changes, make sure
   they pass our test suite which can be started with the following command.

   .. code-block:: bash

       $ pytest

   Sometimes you want to push changes even if the tests fail because you need feedback.
   Then, skip this step.

5. In the next step, try to commit the changes to the branch with an appropriate commit
   message.

   .. code-block:: bash

       $ git commit -am "Changed ... ."

   A commit starts the pre-commits which are additional checks, mostly formatting and
   style checks. If an error occurs, the commit is rejected and you need to review the
   log in your terminal to fix the issues. If an reported error is unclear to you, try
   to use Google for more help. After fixing all issues, you need to commit the changes
   again.

5. If your commit passes, push your changes to the repository. Then, go to either the
   official GETTSIM or your fork's Github page. A banner will be displayed asking you
   whether you would like to create a PR. Follow the link and the instructions of the PR
   template. Fill out the PR form to inform everyone else on what you are trying to
   accomplish and how you did it.

   The PR also starts a complete run of the test suite on a continuous integration
   server. The status of the tests is shown in the PR. You can follow the links to Azure
   Pipelines to get more details on why the tests failed. Reiterate on your changes
   until the tests pass on the remote machine.

6. Ask one of the main contributors to review your changes. Include their remarks in
   your changes.

7. The final PR will be merged by one of the main contributors.
