Testing
#######


The project contains 4 sets of tests:

* Unit tests in ``tests``
* Integration tests in ``tests_integration``
* Module tests in ``tests_module``
* Doctests in ``docs``

Only unit tests are distributed in the package. Unit tests and doctests run automatically on CircleCI.

Unit tests
----------

.. code:: bash

    $ python setup.py test

These tests use pre-recorded betamax cassettes for mocking GitHub API communication. You don't need to set any GitHub credentials to test.

To record cassettes anew, you need to be a member of the ``mi-pyt-ghia`` organization.
Run the following:

.. code:: bash

    $ rm -f tests/fixtures/cassettes/*
    $ export GITHUB_USER=<github user>
    $ export GITHUB_TOKEN=<github token>
    $ cd tests_environment
    $ ./delete.sh && ./setup.sh
    $ cd ..
    $ python setup.py test

Integration tests
-----------------

These tests always use a live repo. To use them you need to be a member of the ``mi-pyt-ghia`` organization.
Run the following:

.. code:: bash

    $ export GITHUB_USER=<github user>
    $ export GITHUB_TOKEN=<github token>
    $ cd tests_environment
    $ ./delete.sh && ./setup.sh
    $ cd ..
    $ python -m pytest tests_integration

Module tests
------------

These tests internally use integration tests so make sure to meet their requirements. Additionally, these tests test repo and package installs.
Run the following:

.. code:: bash

    $ export GITHUB_USER=<github user>
    $ export GITHUB_TOKEN=<github token>
    $ export CTU_USERNAME=<CTU username>
    $ export GHIA_REPO=<full URI to this repo (git@github.com:...)>
    $ cd tests_environment
    $ ./delete.sh && ./setup.sh
    $ cd ..
    $ python -m pytest tests_module

Doctests
--------

These test the code snippets in this documentation.
Make sure you installed the ``dev`` extras (see :ref:`building_docs`).
Run the following:

.. code:: bash

    $ cd docs
    $ make doctest
