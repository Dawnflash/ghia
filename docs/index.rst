.. ghia documentation master file, created by
   sphinx-quickstart on Fri Dec  6 13:23:13 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GHIA: GitHub Issue Assigner
================================

.. image:: https://circleci.com/gh/Dawnflash/ghia.svg?style=shield&circle-token=44975646403e19358f198efec23bd462ae0991db
    :target: https://circleci.com/gh/Dawnflash/ghia

.. toctree::
   :maxdepth: 2
   :caption: Contents

   ghia
   configuration
   usage
   testing
   examples

* Repository: https://github.com/Dawnflash/ghia
* Documentation: https://ghia-zahumada.readthedocs.io/en/latest/

Introduction
############

**GHIA** is a Python package automating the process of GitHub issue assignment.
The package lets you define your own rules for issue assignment and let GHIA handle the rest.
It works both in batch mode as a script and in online mode as a Flask application.

Do I need this?
###############

GitHub lacks a robust method for assigning people to issues based on custom logic.
GHIA lets you define fine-grained regex matchers against issue parts, including labels.
If you seek a way to automate issue assignment on GitHub, give GHIA a try.


Installation
############

GHIA requires Python 3.6.

You can install it from Test PyPI using pip

.. code:: bash

    $ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ghia-zahumada

Alternatively you can clone the repository and run

.. code:: bash

    $ pip install .


.. _assignment_strategy:

Assignment strategy
###################

GHIA supports 3 assignment strategies:

* **append**: add matching users to existing assignees
* **set**: only process unassigned issues
* **change**: replace existing assignees with matching users

The default strategy is always ``append``.


.. _building_docs:

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


.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

