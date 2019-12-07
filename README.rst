GHIA: GitHub Issue Assigner
============================

.. image:: https://circleci.com/gh/Dawnflash/ghia.svg?style=shield&circle-token=44975646403e19358f198efec23bd462ae0991db
    :target: https://circleci.com/gh/Dawnflash/ghia

MI-PYT assignment
#################

**GHIA** is a Python package automating the process of GitHub issue assignment.
The package lets you define your own rules for issue assignment and let GHIA handle the rest.
It works both in batch mode as a script and in online mode as a Flask application.

Author: Adam Zahumensky <zahumada@fit.cvut.cz>

Links
#########

* `Assignment <https://github.com/cvut/ghia>`_
* `Demo webapp <http://ghia.dawnflash.cz>`_
* `Documentation <https://ghia-zahumada.readthedocs.io/en/latest/>`_

Webhook handler mode
--------------------
In this mode the app acts as a webhook receiver for Github.
The default strategy is ``append``.

.. code:: bash

    $ GHIA_DRYRUN=<1|0> \
      GHIA_STRATEGY=<set|change|append> \
      GHIA_CONFIG=<path_a, path_b, ...> \
      FLASK_APP=ghia.py flask run

CLI mode
--------
Batch-process all issues in a single run

.. code:: bash

    $ python -m ghia --help

Building docs
#############

Install the package with the ``dev`` extras. Docs are in the ``docs`` directory.

.. code:: bash

    $ pip install .[dev]
    $ cd docs
    $ make html

License
#######

GHIA is distributed under the MIT license, see LICENSE.
